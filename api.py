# api.py
from fastapi import APIRouter, Request, HTTPException
import os
import requests
import json
from db import Data
from datetime import datetime
from utils import Utils
import threading
from db import WMISDB, DBError

router = APIRouter(prefix="/api")


@router.get("/read/deviceid/{device_id}")
async def read_device(device_id: str):
    u = Utils()
    url = u.build_url_deviceid(device_id)
    headers = u.build_headers()
    payload = {}
    response = requests.get(url, headers=headers, data=payload)

    if response.status_code == 200:
        formatted_json = u.reformat_json(response.text)
        return {"data": formatted_json}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


@router.get("/read/socketid/{socket_id}")
async def read_socket(socket_id: str):
    u = Utils()
    url = u.build_url_socketid(socket_id)
    headers = u.build_headers()
    payload = {}
    response = requests.get(url, headers=headers, data=payload)
    if response.status_code == 200:
        formatted_json = u.reformat_json(response.text)
        return {"data": formatted_json}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


@router.get("/save-last-reading/{socket_id}", status_code=201)
async def save_last_reading(socket_id: str) -> dict:
    u = Utils()
    url = u.build_url_socketid(socket_id)
    headers = u.build_headers()
    payload = {}
    response = requests.get(url, headers=headers, data=payload)
    code = response.status_code
    if 200 <= code < 300:
        data = json.loads(response.text)
        db = Data()
        meter_id = data['socketId']
        reading = data['lastReading']
        reading_date = data['lastReadingDateTime']

        rslt, code = db.insert_reading(meter_id=meter_id, reading_date=reading_date, reading=reading)
        datarslt, datacode = db.insert_ami_data(meter_id=meter_id, reading_date=reading_date, reading=reading,
                                                data=data)

        if rslt == "Ok":
            msg = "Success"
        else:
            msg = rslt
        db = None

        if code != 201:
            raise HTTPException(status_code=code, detail=msg)
        else:
            return {"detail": msg}


@router.get("/last-reading/{socket_id}")
async def last_reading(socket_id: str):
    u = Utils()
    url = u.build_url_socketid(socket_id)
    headers = u.build_headers()
    payload = {}
    response = requests.get(url, headers=headers, data=payload)
    if response.status_code != 200:
        rslt = {
            'device_id': '',
            'turnout_id': socket_id,
            'reading': 0,
            'timestamp': ''
        }
        msg = "Socket ID not found"
        code = response.status_code
    else:
        data = json.loads(response.text)
        rslt = {
            'device_id': data['deviceId'],
            'turnout_id': data['socketId'],
            'reading': data['lastReading'],
            'timestamp': data['lastReadingDateTime']
        }
        msg = "Success"
        code = 200

    if code == 200:
        return {"data": rslt, "message": msg}
    else:
        raise HTTPException(status_code=code, detail=msg)


@router.get("/meter-list")
async def meter_list():
    db = Data()
    lst = db.ami_meter_list()
    db = None
    return {"data": lst}


@router.get("/save-last-readings/all")
async def save_last_readings(request: Request):
    cmdlist = []
    semaphore = threading.Semaphore(10)
    cmdlist_lock = threading.Lock()

    db = Data()
    lst = db.ami_meter_list()
    # # modify lst to contain the first 10 items
    # lst = lst[:20]
    db = None


    def worker(socket_id):
        with semaphore:
            cmd = Utils().load_and_save_last_reading(socket_id=socket_id)
            with cmdlist_lock:
                cmdlist.append(cmd)
                print(f'Processed {socket_id}', end='\r')

    threads = []
    for item in lst:
        t = threading.Thread(target=worker, args=(item['meter_id'],))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print('done processing all readings')

    cmds = []
    for c in cmdlist:
        if c is not None:
            for item in c:
                if item['cmd'] > '':
                    cmds.append(item)


    # now process the inserts
    wmisdb = WMISDB()
    conn = wmisdb.connection
    cursor = conn.cursor()
    conn.autocommit = False

    inserted = 0
    errors = 0
    for item in cmds:
        try:
            if item['cmd'] > '':
                cursor.execute(item['cmd'])
                inserted += 1
        except DBError as err:
            print(f"DBError: {err}\r{item['cmd']}")
            errors += 1
        except Exception as err:
            print(f"Error: {err}\r{item['cmd']}")
            errors += 1


    conn.commit()
    wmisdb = None
    msg = f'Inserted {inserted} records with {errors} errors'
    return {"message": msg}
