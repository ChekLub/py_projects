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

my_token = '643979**********************Ialk' #  токен вашего бота
bot = telegram.Bot(token=my_token) # получаем доступ
chat_id = ##########  

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

# Дефолтные параметры, которые прокидываются в таски
default_args = {
    'owner': 'l-chekletsova',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 8, 15), #date.today() - timedelta(1),
}
# Интервал запуска DAG
schedule_interval = '00 11 * * *'

@dag(default_args=default_args, schedule_interval=schedule_interval, catchup=False)
def dag_report_2_chekletsova():
    
    @task
    def extract_metrics():
        q = """
        SELECT  toDate(time) date,
                count(distinct user_id) dau,
                countIf(action='like') likes,
                countIf(action='view') views,
                countIf(user_id, action = 'like') / countIf(user_id, action = 'view') ctr
        FROM simulator_20230720.feed_actions 
        WHERE date >= today() - 7 and date < today() 
        GROUP BY date
        ORDER BY date
        """
        metrics = pandahouse.read_clickhouse(q, connection=connection_read)
        return metrics
    
    @task
    def extract_avg_actions():
        q = """
        select avg(action_by_user) avg_actions_per_user, date
            from (
                select  count(action) action_by_user, toDate(time) date
                from simulator_20230720.feed_actions
                where date >= today() - 7
                group by user_id, date
                order by date )
            group by date
        """
        avg_actions = pandahouse.read_clickhouse(q, connection=connection_read)
        return avg_actions
    
    @task
    def plot_metrics(metrics, avg_actions):
        plt.figure(figsize=(16, 8))
        plt.suptitle('Основные метрики за неделю')
        plt.subplot(2, 2, 1)
        sns.lineplot(x= metrics.date, y=metrics.dau, marker = 'o')
        plt.xticks(rotation=15)
        plt.ylabel('DAU')
        plt.xlabel('')
        plt.grid()

        plt.subplot(2, 2, 2)

        sns.lineplot(x= metrics.date, y=metrics.views, marker = 'o', label = 'Просмотры')
        sns.lineplot(x= metrics.date, y=metrics.likes, marker = 'o',  color='r', label = 'Лайки')
        plt.xticks(rotation=15)
        plt.ylabel('Активности')
        plt.xlabel('')
        plt.legend()
        plt.grid()

        plt.subplot(2, 2, 3)

        sns.lineplot(x= metrics.date, y=metrics.ctr, marker = 'o')
        plt.xticks(rotation=15)
        plt.ylabel('CTR')
        plt.xlabel('')
        plt.grid()

        plt.subplot(2, 2, 4)

        sns.lineplot(x = avg_actions['date'], y = avg_actions['avg_actions_per_user'],  marker = 'o')
        plt.xticks(rotation=15)
        plt.ylabel('Средняя активность пользователей')
        plt.xlabel('')
        plt.grid()

        plot_object = io.BytesIO()
        plt.savefig(plot_object)
        plot_object.seek(0)
        plot_object.name = 'Metrics.png'
        plt.close()
        bot.sendPhoto(chat_id=chat_id, photo=plot_object)
        #plt.show()

    @task
    def extract_new_users():
        q = """
        SELECT str_date AS Date,
               str_start_date AS Start_date,
               max(users) AS Users
        FROM
          (select count(DISTINCT user_id) users,
                  toString(start_date) str_start_date,
                  toString(date) str_date,
                  start_date, date
           from
             (select DISTINCT user_id,
                    toDate(time) date
              from simulator_20230720.feed_actions) users_date
           join
             (SELECT user_id,
                     min(toDate(time)) start_date
              from simulator_20230720.feed_actions
              GROUP by user_id) as start_dates using user_id
               where start_date >= today() - 7
           group by date, start_date) AS virtual_table
        GROUP BY Date, Start_date
        ORDER BY Start_date
        """
        df = pandahouse.read_clickhouse(q, connection=connection_read)
        return df
    
    @task
    def plot_heat_map_retantion(df):
        df = df.pivot(index = 'Start_date', columns= 'Date', values='Users')
        
        plt.figure(figsize=(16, 8))
        sns.heatmap(df, annot=True, cmap="crest", fmt=".0f",  linewidth=.5)
        plt.title('Динамика по когортам пользователей, пришедших за неделю')
        
        plot_object = io.BytesIO()
        plt.savefig(plot_object)
        plot_object.seek(0)
        plot_object.name = 'heat_map.png'
        plt.close()
        bot.sendPhoto(chat_id=chat_id, photo=plot_object)

    @task
    def extract_report_yeasterday():
        q = """
            select * from test.dag_chekletsova_cohorts_age_7_00
            """
        report = pandahouse.read_clickhouse(q, connection=connection_load)
        return report

    @task
    def print_report_yeasterday(report):
        msg = f'Сводная таблица активностей пользователей мессенджера и ленты новостей за вчера прикреплена в файле report.csv'
        bot.sendMessage(chat_id=chat_id, text=msg)
        
        file_object = io.StringIO()
        report.to_csv(file_object)
        file_object.name = 'report.csv'
        file_object.seek(0)
        bot.sendDocument(chat_id=chat_id, document=file_object)

    @task
    def print_metrics(metrics, new_users):
        date = str(metrics.iloc[-1].date).split(' ')[0]
        msg = f'Показания ключевых метрик за {date}: \nНовых пользователей: {new_users} \nDAU: {metrics.iloc[-1]["dau"]} \nLikes: {metrics.iloc[-1]["likes"]} \nViews: {metrics.iloc[-1]["views"]} \nCTR: {metrics.iloc[-1]["ctr"]:.4f} '
        bot.sendMessage(chat_id=chat_id, text=msg)
        
    metrics = extract_metrics()
    new_users = extract_new_users()
    avg_actions = extract_avg_actions()
    report_yeasterday = extract_report_yeasterday()
    
    print_metrics(metrics, new_users.iloc[-1].Users)
    plot_metrics(metrics, avg_actions)
    plot_heat_map_retantion(new_users)
    print_report_yeasterday(report_yeasterday)

dag_report_2_chekletsova = dag_report_2_chekletsova()


