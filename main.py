import paho.mqtt.client as mqtt
import json
import os
from dotenv import load_dotenv
import requests
import pandas as pd
import datetime
from dotenv import load_dotenv,set_key
from pathlib import Path
import pymssql
import random


load_dotenv()

mqtt_broker = os.getenv('MQTT_BROKER')
mqtt_port = int(os.getenv('MQTT_PORT'))
mqtt_topic = os.getenv('MQTT_TOPIC')

sql_server = os.getenv('SQL_SERVER')
sql_username = os.getenv('SQL_USERNAME')
sql_password = os.getenv('SQL_PASSWORD')
sql_database = os.getenv('SQL_DATABASE')
sql_table = os.getenv('SQL_TABLE')
sql_table_loc = os.getenv('SQL_TABLE_LOC')



url = os.getenv('URL_1')

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode('utf-8'))

    # param
    req_code =  f'req_{random.randint(100,10000)}' #### need generate
    rfid_data = payload["rfid"]
    status_init = 99
    position_code_1 = os.getenv("POSITIONCODE_1")
    position_code_2 = str(query_location(rfid_data))
    tasktyp = os.getenv("TASKTYP")
    type1 = os.getenv("TYPE_1")
    type2 = os.getenv("TYPE_2")
    map_code = os.getenv("MAPCODE")

    agv_cmd = {"reqCode":f'{req_code}',
    "taskTyp":f'{tasktyp}',
    "positionCodePath":[{
        "positionCode": f'{position_code_1}',
        "type": f'{type1}'
    },
    {
        "positionCode": f'{position_code_2}',
        "type": f'{type2}'
    }],
        "mapCode":f'{map_code}'
    }
    agv_cmd_json = json.dumps(agv_cmd)
    print(agv_cmd_json)
    response = requests.post(url, json=agv_cmd_json)

    if response.status_code == 200:
        print('Request was successful.')
        print('Response:', response.json())
        job_data = response.json()['data']
        print(job_data)
        insert_sql(job_data,rfid_data,req_code,status_init,position_code_1,position_code_2)
    else:
        print(f'Failed with status code: {response.status_code}')
        print('Response:', response.text)

def query_location(rfid):
    try:
        conn = pymssql.connect(server=sql_server, user=sql_username, password=sql_password, database=sql_database)
        cursor = conn.cursor()
        query = f"""SELECT * FROM {sql_table_loc} where rfid_tag ='{rfid}'"""
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(results, columns=columns)
        location = df['loc_wh'].values[0]
        return location

    except pymssql.DatabaseError as e:
        print("Database error:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def insert_sql(job_data,rfid_data,req_code,status,loc_1,loc_2):
    try:
        conn = pymssql.connect(server=sql_server, user=sql_username, password=sql_password, database=sql_database)
        cursor = conn.cursor()
        query = f"""INSERT INTO {sql_table} (job_data, rfid_data,req_code ,status,loc_1,loc_2,register) VALUES (%s, %s, %s, %s,%s, %s,GETDATE())"""
        cursor.execute(query, (job_data,rfid_data,req_code,status,loc_1,loc_2))
        conn.commit() 
        print("Inserted successfully")
    
    except pymssql.DatabaseError as e:
        print("Database error:", e)
    
    finally:
        cursor.close()
        conn.close()

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(mqtt_broker, mqtt_port, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()