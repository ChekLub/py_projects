import telegram
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
from read_db.CH import Getch
import pandas as pd
import pandahouse 
from datetime import datetime, timedelta, date
from io import StringIO
import requests

my_token = '64***********************XAb9DnAOhIalk' # токен вашего бота
bot = telegram.Bot(token=my_token) # получаем доступ
chat_id = ############ #  

connection_read = {
    'host': 'https://clickhouse.lab.karpov.courses',
    'password': '****',
    'user': '****',
    'database': 'simulator_20230720'
}

connection_load = {
            'host': 'https://clickhouse.lab.karpov.courses',
            'password': '****',
            'user': '****',
            'database': 'test'
            }


q = """select users_feed,
       users_message,  
       likes,
       views,
       ctr,
       sended_message, 
       times,
       toDate(times) date,
       hr
from 

  (select count (DISTINCT user_id) users_feed,
          COUNTIf(action = 'like')  likes,
          COUNTIf(action = 'view')  views,
          likes/views ctr,
          toStartOfFifteenMinutes(time) times,
          formatDateTime(times, '%R') hr
  from simulator_20230720.feed_actions 
  WHERE  (toDate(time) >= today() - 1) and  (time < toStartOfFifteenMinutes(now()))
  GROUP BY times
  order by times desc ) fa

join 

  (select COUNT (reciever_id) as sended_message,
          count (DISTINCT user_id) users_message,
          toStartOfFifteenMinutes(time) times,
          formatDateTime(times, '%R') hr
  from simulator_20230720.message_actions 
  WHERE  (toDate(time) >= today() - 1) and  (time < toStartOfFifteenMinutes(now()))
  GROUP BY times
  order by times desc ) ma 
using times
order by times 
"""

def check_anomaly(df, metric, a=3, n=4):
    df['q25'] = df[metric].shift(1).rolling(n).quantile(0.25)
    df['q75'] = df[metric].shift(1).rolling(n).quantile(0.75)
    df['iqr'] = df['q75'] - df['q25']
    df['up'] = df['q75'] + a * df['iqr']
    df['low'] = df['q25'] - a * df['iqr']
        
    df['up'] = df['up'].rolling(n, center= True, min_periods= 1).mean()
    df['low'] = df['low'].rolling(n, center= True, min_periods= 1).mean()
        
    if df[metric].iloc[-1] < df['low'].iloc[-1] or df[metric].iloc[-1] > df['up'].iloc[-1]:
        is_alert = True
    else:
        is_alert = False
        
    return is_alert, df

# Дефолтные параметры, которые прокидываются в таски
default_args = {
    'owner': 'l-chekletsova',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 8, 18), #date.today() - timedelta(1),
}
# Интервал запуска DAG
schedule_interval = '/15 * * * *'

@dag(default_args=default_args, schedule_interval=schedule_interval, catchup=False)
def dag_alert_chekletsova():
    
    @task
    def run_alert():        
        data = pandahouse.read_clickhouse(q, connection=connection_read)
        
        metrics = ['users_feed', 'users_message', 'likes', 'views', 'ctr', 'sended_message']
        
        count_alerts = 0
        for metric in metrics:
            df = data[['times', 'hr', metric]].copy()
            
            if metric != 'ctr':
                is_alert, df_metric = check_anomaly(df, metric, a=3, n=8)
            else:
                is_alert, df_metric = check_anomaly(df, metric, a=2, n=10)
            
            if is_alert:
                if count_alerts == 0:
                    msg = f'Внимание! Обнаружено отклонение в метриках. Проанализируйте, пожалуйста.\nДашборд можно открыть по ссылке {"http://superset.lab.karpov.courses/r/4263"}'
                    bot.sendMessage(chat_id=chat_id, text=msg)
                
                count_alerts += 1
                
                msg = f'Метрика: {metric}\nТекущее значение: {df_metric[metric].iloc[-1]:.2f}\nОтклонение от предыдущего значения: {(1 - df_metric[metric].iloc[-1] / df_metric[metric].iloc[-2]):.2f}%'
                bot.sendMessage(chat_id=chat_id, text=msg)
                
                plt.figure(figsize=(16, 8))
                ax = sns.lineplot(x= df_metric['times'], 
                             y= df_metric[metric], 
                             marker = 'o')
                
                plt.fill_between(x= df_metric['times'], 
                                 y1= df_metric['up'], 
                                 y2= df_metric['low'],
                                 alpha= 0.2)
                
                plt.xticks(df_metric['times'], df_metric['hr'])
                
                for ind, label in enumerate(zip(ax.get_xgridlines(), ax.get_xticklabels())):
                    if ind % 10 == 0:
                        label[0].set_visible(True)
                        label[1].set_visible(True)
                    else:
                        label[0].set_visible(False)
                        label[1].set_visible(False)
        
                plt.ylabel(metric)
                plt.xlabel('Время')
                plt.title(metric)
                plt.legend([metric, 'доверительный интервал'])
                
                plot_object = io.BytesIO()
                plt.savefig(plot_object)
                plot_object.seek(0)
                plot_object.name = 'Metrics.png'
                plt.close()
                bot.sendPhoto(chat_id=chat_id, photo=plot_object)
                
            
    run_alert()

dag_alert_chekletsova = dag_alert_chekletsova()
