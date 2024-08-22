import dotenv
from fastapi import FastAPI
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

app = FastAPI()

@app.get("/api/read/deviceid/{device_id}")
async def read_device(device_id: str):
    url = build_url_deviceid(device_id)
    headers = build_headers()
    payload = {}
    response = requests.get(url, headers=headers, data=payload)
    formatted_json = reformat_json(response.text)
    return {"data": formatted_json}

def build_url_deviceid(id:str) -> str :
    from datetime import datetime, timedelta
    # determine datefrom and dateto where datefrom is yesterday and dateto is today
    today = datetime.utcnow()
    yesterday = today - timedelta(1)
    datefrom = yesterday.strftime('%Y-%m-%dT00:00:00.000Z')
    dateto = today.strftime('%Y-%m-%dT00:00:00.000Z')
    url = os.getenv('APIURL') + os.getenv('COMPANYID')  + '/devices/report'
    url = url + f"?DeviceIds={id}00&Parameters=Consumption&Parameters=Reading&"
    url = url + f"DateInterval=Daily&"
    url = url + f"startDate={datefrom}&endDate={dateto}"
    return url

def build_headers() -> dict:
    key = os.getenv('APIKEY')
    headers = {
        'authorization': key
    }
    return headers

def reformat_json(json_data: str) -> str:
    data = json.loads(json_data)
    formatted_data = json.dumps(data, indent=4)
    return formatted_data

@app.get("/api/read/socketid/{socket_id}")
async def read_socket(socket_id: str):
    url = build_url_socketid(socket_id)
    headers = build_headers()
    payload = {}
    response = requests.get(url, headers=headers, data=payload)
    formatted_json = reformat_json(response.text)

    return {"data": formatted_json}

def build_url_socketid(socket_id:str) -> str :
    # does not work since socket id is not a parameter in the API
    from datetime import datetime, timedelta
    today = datetime.utcnow()
    yesterday = today - timedelta(1)
    datefrom = yesterday.strftime('%Y-%m-%dT00:00:00.000Z')
    dateto = today.strftime('%Y-%m-%dT00:00:00.000Z')

    url = os.getenv('APIURL') + os.getenv('COMPANYID') + '/sockets/report'
    url = url + f"?socketid={socket_id}&Parameters=Consumption&Parameters=Reading&"
    url = url + f"DateInterval=Daily&"
    url = url + f"startDate={datefrom}&endDate={dateto}"
    return url

@app.get("/")
async def root():
    return {"message": ""}


