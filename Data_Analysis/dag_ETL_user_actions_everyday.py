# coding=utf-8
import pandas as pd
import pandahouse 
from datetime import datetime, timedelta, date
from io import StringIO
import requests

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context

connection_read = {
    'host': 'https://clickhouse.lab.karpov.courses',
    'password': '****',
    'user': '****',
    'database': 'simulator_20230720'
}

def ch_get_df(query, connection):
    return pandahouse.read_clickhouse(query=query, connection=connection)

# Дефолтные параметры, которые прокидываются в таски
default_args = {
    'owner': 'l-chekletsova',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 8, 15), #date.today() - timedelta(1),
}

# Интервал запуска DAG
schedule_interval = '00 7 * * *'

@dag(default_args=default_args, schedule_interval=schedule_interval, catchup=False)
def dag_chekletsova_cohorts_age_7_00():

    @task() 
    def extract_feed():
        # В feed_actions для каждого юзера посчитаем число просмотров и лайков контента.
        q = """
        SELECT toDate(time) event_date,
               user_id ,
               COUNTIf(action = 'like')  likes,
               COUNTIf(action = 'view')  views,
               gender ,
               age ,
               os
        FROM simulator_20230720.feed_actions
        WHERE toDate(time) = today() - 1
        GROUP BY user_id , event_date, gender, age, os
        """
        df_cube = ch_get_df(query=q, connection=connection_read)
        return df_cube
    
    @task() 
    def extract_message():
        # В message_actions для каждого юзера считаем, сколько он получает и отсылает сообщений, скольким людям он пишет, сколько людей пишут ему.
        q =  """
        select t3.event_date event_date,
               reciever_id user_id,
               messages_received,
               messages_sent,
               users_received,
               users_sent,
               t3.gender gender,
               t3.os os,
               t3.age age
        from 
          (SELECT user_id ,
                 toDate(time) event_date ,  
                 COUNT (DISTINCT reciever_id) as users_sent, 
                 COUNT (reciever_id) as messages_sent 
          FROM simulator_20230720.message_actions 
          WHERE toDate(time) = today() - 1
          GROUP BY event_date , user_id 
          ) t0
        RIGHT join 
          (SELECT reciever_id, event_date, users_received, messages_received, age , gender, os
          from 
              (SELECT reciever_id ,
                      toDate(time) event_date ,  
                      COUNT (DISTINCT user_id) as users_received,
                      COUNT (user_id) as messages_received
       
              FROM simulator_20230720.message_actions 
              WHERE toDate(time) = today() - 1
              GROUP BY event_date, reciever_id) t1
          join 
              (SELECT DISTINCT user_id, 
                      age, gender, os 
              from simulator_20230720.message_actions) t2
          on t1.reciever_id = t2.user_id
          ) t3
        on t3.reciever_id = t0.user_id
        
        """ 
        
        df_cube = ch_get_df(query=q, connection=connection_read)
        return df_cube
    
    @task()
    def transform_merge_cubes(df_cube_1, df_cube_2):
        df_cube = df_cube_1.merge(df_cube_2, 
                                  left_on=['user_id', 'event_date', 'gender', 'os', 'age'], 
                                  right_on=['user_id', 'event_date', 'gender', 'os', 'age'], 
                                  how='outer')
        df_cube.fillna(0, inplace=True)
        return df_cube
    
    @task
    def transform_gender(df_cube):
        df_cube_gender = df_cube[['event_date', 'gender', 'views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent']]\
                         .groupby(['event_date', 'gender'])\
                         .sum()\
                         .reset_index()
        df_cube_gender.insert(1, 'dimension', ['gender', 'gender'])
        df_cube_gender.rename(columns={'gender' : 'dimension_value'}, inplace=True)
        return df_cube_gender
    
    @task
    def transform_os(df_cube):
        df_cube_os = df_cube[['event_date', 'os', 'views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent']]\
                    .groupby(['event_date', 'os'])\
                    .sum()\
                    .reset_index()
        
        df_cube_os = df_cube_os.melt(id_vars=['event_date', 'views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent'],
                                    value_vars='os',
                                    var_name='dimension',
                                    value_name='dimension_value')
        
        df_cube_os = df_cube_os[['event_date', 'dimension',  'dimension_value', 'views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent']]
        return df_cube_os
    
    @task
    def transform_age(df_cube):
        df_cube['age_cohorts'] = '..'
        df_cube.loc[df_cube['age'] <= 18, 'age_cohorts'] = '..18'
        df_cube.loc[(df_cube['age'] > 18) & (df_cube['age'] <= 25), 'age_cohorts'] = '19..25'
        df_cube.loc[(df_cube['age'] > 25) & (df_cube['age'] <= 35), 'age_cohorts'] = '26..35'
        df_cube.loc[(df_cube['age'] > 35) & (df_cube['age'] <= 45), 'age_cohorts'] = '36..45'
        df_cube.loc[(df_cube['age'] > 45) & (df_cube['age'] <= 55), 'age_cohorts'] = '46..55'
        df_cube.loc[(df_cube['age'] > 55), 'age_cohorts'] = '56..'
        df_cube_cohorts = df_cube.drop('age', axis=1)
        df_cube_cohorts.rename(columns={'age_cohorts': 'age'}, inplace=True)
    
        df_cube_age = df_cube_cohorts[['event_date', 'age', 'views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent']]\
                     .groupby(['event_date', 'age'])\
                     .sum()\
                     .reset_index()
        
        df_cube_age = df_cube_age.melt(id_vars=['event_date', 'views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent'],
                                      value_vars='age',
                                      var_name='dimension',
                                      value_name='dimension_value')
        
        df_cube_age = df_cube_age[['event_date', 'dimension',  'dimension_value', 'views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent']]
        return df_cube_age
    
    @task
    def transform_concat(df_cube_gender, df_cube_age, df_cube_os):
        df_cube_concat = pd.concat([df_cube_os, df_cube_gender, df_cube_age], axis=0, ignore_index=True)
        df_cube_concat = df_cube_concat.astype({'views': 'uint32', 'likes': 'uint32', 'messages_received': 'uint32',\
                                                'messages_sent': 'uint32', 'users_received': 'uint32', 'users_sent': 'uint32'})
        return df_cube_concat
    
    @task
    def load(df_cube):
        connection_load = {
            'host': 'https://clickhouse.lab.karpov.courses',
            'password': '656e2b0c9c',
            'user': 'student-rw',
            'database': 'test'
            }
        
        q_create = """
                    create table if not exists test.dag_chekletsova_cohorts_age_7_00
                    (
                        event_date Date, 
                        dimension String,
                        dimension_value String,
                        views UInt32,
                        likes UInt32,
                        messages_received UInt32,
                        messages_sent UInt32,
                        users_received UInt32,
                        users_sent UInt32
                    ) engine = MergeTree() 
                    order by event_date
                 """
        pandahouse.execute(q_create, connection=connection_load, data=None, external=None, stream=False)
        pandahouse.to_clickhouse(df=df_cube, table='dag_chekletsova_cohorts_age_7_00', connection=connection_load, index=False)

        context = get_current_context()
        ds = context['ds']
        print(f'Actions for {ds}')
        print(df_cube.to_csv(index=False, sep='\t'))

        
    df_cube_feed = extract_feed()
    df_cube_message = extract_message()
    
    df_cube = transform_merge_cubes(df_cube_feed, df_cube_message)
    df_cube_gender = transform_gender(df_cube)
    df_cube_age = transform_age(df_cube)
    df_cube_os = transform_os(df_cube)
    df_cube_union = transform_concat(df_cube_gender, df_cube_age, df_cube_os)
    load(df_cube_union)

dag_chekletsova_cohorts_age_7_00 = dag_chekletsova_cohorts_age_7_00()