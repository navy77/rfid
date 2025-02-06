import paho.mqtt.client as mqtt
import json
import os
from dotenv import load_dotenv
import requests
import pandas as pd
from datetime import datetime
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

    rfid_data = payload["rfid"]
    run(rfid_data)

def genAgvSchedulingTask(reqCode,rfid_data,location2):

    status_init = 99
    position_code_1 = os.getenv("POSITIONCODE_1")
    position_code_2 = location2

    tasktyp = os.getenv("TASKTYP")
    type1 = os.getenv("TYPE_1")
    type2 = os.getenv("TYPE_2")
    map_code = os.getenv("MAPCODE")
    map_short_name = os.getenv("MAPShortName")

    cmd_json = {"reqCode":f'{reqCode}',
    "taskTyp":f'{tasktyp}',
    "positionCodePath":[{
        "positionCode": f'{position_code_1}',
        "type": f'{type1}'
    },
    {
        "positionCode": f'{position_code_2}',
        "type": f'{type2}'
    }],
        "mapCode":f'{map_code}',
        "mapShortName":f'{map_short_name}'
    }
    # cmd_json = json.dumps(cmd_json)
    # print(cmd_json)
    url = os.getenv("URL_2")
    response = requests.post(url, json=cmd_json)

    if response.status_code == 200:
        print('Request agvgen successful.')
        print('Response:', response.json())
        job_data = response.json()['data']

        insert_sql(job_data,rfid_data,reqCode,status_init,position_code_1,position_code_2)

    else:
        print(f'Failed with status code: {response.status_code}')
        print('Response:', response.text)

def bindCtnrAndBin(reqCode,stgbincode):
    url = os.getenv("URL_1")
    cmd_json = {
    "reqCode":reqCode,
    "ctnrTyp": os.getenv("CTNRTYP"),
    "stgBinCode": stgbincode,
    "indBind": os.getenv("INDBIND")
    }

    response = requests.post(url, json=cmd_json)
    if response.status_code == 200:
        print('Request bindctnr successful.')
        return 1
    else:
        print(f'Failed status code: {response.status_code}')
        print('Response:', response.text)
        return 0

def query_location(rfid):
    try:
        conn = pymssql.connect(server=sql_server, user=sql_username, password=sql_password, database=sql_database)
        cursor = conn.cursor()
        query = f"""SELECT * FROM {sql_table_loc} where rfid_code ='{rfid}'"""
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(results, columns=columns)
        location = df['location_name'].values[0]
        stgbincode = df['stgbin_code'].values[0]

        return location,stgbincode

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
        print(query)
        cursor.execute(query, (job_data,rfid_data,req_code,status,loc_1,loc_2))
        conn.commit() 
        print("Inserted successful")
    
    except pymssql.DatabaseError as e:
        print("Database error:", e)
    
    finally:
        cursor.close()
        conn.close()

def run(rfid_data):
    req_code = f'r_{datetime.now().strftime("%Y%m%d%H%M%S")}'

    stgbincode = os.getenv("STGBINCODE")
    bind_status = bindCtnrAndBin(req_code,stgbincode)
    location2,stgbincode = query_location(rfid_data)

    if bind_status==1:
        genAgvSchedulingTask(req_code,rfid_data,location2)

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(mqtt_broker, mqtt_port, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()