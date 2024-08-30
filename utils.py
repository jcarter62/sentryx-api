import os
import requests
import json
from db import Data
from datetime import datetime


def load_and_save_last_reading(socket_id: str):
    url = build_url_socketid(socket_id)
    headers = build_headers()
    payload = {}
    response = requests.get(url, headers=headers, data=payload)
    code = response.status_code
    if 200 <= code < 300:
        data = json.loads(response.text)
        db = Data()
        meter_id = data['socketId']
        reading = data['lastReading']
        reading_date = data['lastReadingDateTime']
        rd_type = data['productType']
        rd_status = data['deviceStatus']
        rd_unit = data['units']
        rd_source = data['deviceId']
        if not_valid_data(reading_date, reading):
            # skip this record
            msg = "Invalid data"
        else:
            try:
                rslt, code = db.insert_reading(
                    meter_id=meter_id, reading_date=reading_date, reading=reading,
                    rd_type=rd_type, rd_status=rd_status, rd_unit=rd_unit, rd_source=rd_source)
            finally:
                pass
            if rslt == "Ok":
                msg = "Success"
            else:
                msg = rslt
        db = None
        print(f"{meter_id} - {reading_date} - {reading} - {msg}")

        return {"detail":msg, "status_code": code}

def not_valid_data(dt: str, reading: float) -> bool:
    rslt = False
    if not_valid_datetime(dt) or not_valid_reading(reading):
        rslt = True
    return rslt

def not_valid_reading(reading: float) -> bool:
    if (reading < 0) or (reading > 100000000):
        return True
    else:
        return False

def not_valid_datetime(date_text: str) -> bool:
    try:
        if date_text is None or date_text == '':
            return True
        datetime.fromisoformat(date_text)
        return False
    except Exception as e:
        print(f'Error in not_valid_datetime: {e}')
        return True

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

def build_url_socketid(socket_id:str) -> str :
    # does not work since socket id is not a parameter in the API
    from datetime import datetime, timedelta
    today = datetime.utcnow()
    yesterday = today - timedelta(1)

    url = os.getenv('APIURL') + os.getenv('COMPANYID')
    url = url + f"/sockets/{socket_id}"
    return url
