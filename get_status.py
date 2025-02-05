import pymssql
import requests
import json
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

url = os.getenv('URL_2')

sql_server = os.getenv('SQL_SERVER')
sql_username = os.getenv('SQL_USERNAME')
sql_password = os.getenv('SQL_PASSWORD')
sql_database = os.getenv('SQL_DATABASE')
sql_table = os.getenv('SQL_TABLE')

def query_mssql():
    try:
        conn = pymssql.connect(server=sql_server, user=sql_username, password=sql_password, database=sql_database)
        cursor = conn.cursor()
        query = f"""SELECT * FROM {sql_table} where status !='0'"""  # 0= success
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(results, columns=columns)
        return df
    except pymssql.DatabaseError as e:
        print("Database error:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_status(df):
    for _, row in df.iterrows():
        agv_status_json = {"reqCode": row['req_code'],"taskCodes": row['job_data']}
        job_data = row['job_data']
        response = requests.post(url, json=agv_status_json)
        if response.status_code == 200:
            result_agv = str(response.json()['code'])
            if result_agv == '0':
                update_sql(result_agv,job_data)
                print('Response:', response.json())
                print('Request was successful')
        else:
            print(f'Failed with status code: {response.status_code}')
            print('Response:', response.text)    

def update_sql(result_agv,job_data):
    try:
        conn = pymssql.connect(server=sql_server, user=sql_username, password=sql_password, database=sql_database)
        cursor = conn.cursor()
        query = f"""update {sql_table} set status = {result_agv} where job_data ='{job_data}'"""
        cursor.execute(query)
        conn.commit() 
    except pymssql.DatabaseError as e:
        print("Database error:", e)
    finally:
        cursor.close()
        conn.close()

def main():
    df_query = query_mssql()
    get_status(df_query)

if __name__ == "__main__":
    main()