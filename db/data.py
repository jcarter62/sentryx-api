import os.path
from .wmisdb import WMISDB, DBError
from dotenv import load_dotenv
import os

load_dotenv()

class Data:
    def __init__(self):
        if not self.__table_exists__():
            self.__create_table__()

    # table name: ami_readings, columns
    # meter_id, reading_date, reading_time, reading_value, reading_type, reading_status, reading_unit, reading_source

    def __table_exists__(self) -> bool:
        rslt = False
        try:
            wmisdb = WMISDB()
            conn = wmisdb.connection
            cursor = conn.cursor()
            cmd = 'select count(*) from information_schema.tables where table_name = \'ami_readings\';'
            cursor.execute(cmd)
            rows = cursor.fetchall()
            if rows[0][0] == 1:
                rslt = True
            else:
                rslt = False
            wmisdb = None
        except DBError as err:
            print(f'Error in determine_if_table_exists {err}')
            rslt = False
        except Exception as err:
            print(f'Unexpected Error: {err}')
            rslt = False
        return rslt

    def __create_table__(self) -> bool:
        rslt = False
        try:
            wmisdb = WMISDB()
            conn = wmisdb.connection
            cursor = conn.cursor()
            # open create_ami_readings.sql and read the contents into cmd
            sql_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'create_ami_readings.sql')
            with open(sql_file, 'r') as file:
                cmd = file.read()
            cursor.execute(cmd)
            conn.commit()
            wmisdb = None
            rslt = True
        except DBError as err:
            print(f'Error in create_table {err}')
            rslt = False
        except Exception as err:
            print(f'Unexpected Error: {err}')
            rslt = False
        return rslt

    def insert_reading(self, meter_id: str, reading_date: str, reading: float,
                       rd_type: str = '', rd_status: str = '', rd_unit: str = '', rd_source: str = '') -> tuple[str, int]:
        rslt = ''
        try:
            wmisdb = WMISDB()
            conn = wmisdb.connection
            cursor = conn.cursor()
            # check to see if the reading already exists
            cmd = f'select count(*) from ami_readings where meter_id = \'{meter_id}\' and reading_dt = \'{reading_date}\';'
            cursor.execute(cmd)
            rows = cursor.fetchall()
            if rows[0][0] > 0:
                rslt = "Reading already exists"
                code = 208
            else:
                cmd = f'insert into ami_readings (meter_id, reading_dt, reading, rd_type, rd_status, rd_unit, rd_source) ' + \
                      f'values (\'{meter_id}\', \'{reading_date}\', {reading}, ' + \
                      f' \'{rd_type}\', \'{rd_status}\', \'{rd_unit}\', \'{rd_source}\' );'
                cursor.execute(cmd)
                conn.commit()
                wmisdb = None
                rslt = "Ok"
                code = 201

        except DBError as err:
            rslt = f'Error in insert_reading {err}'
            code = 500
        except Exception as err:
            rslt = f'Unexpected Error: {err}'
            code = 500
        return rslt, code

    def find_reading(self, meter_id: str, reading_date: str) -> dict:
        rslt = {}
        try:
            wmisdb = WMISDB()
            conn = wmisdb.connection
            cursor = conn.cursor()
            cmd = f'select * from ami_readings where meter_id = \'{meter_id}\' and reading_date = \'{reading_date}\';'
            cursor.execute(cmd)
            rows = cursor.fetchall()
            if len(rows) > 0:
                rslt = rows[0]
            else:
                rslt = {}
            wmisdb = None
        except DBError as err:
            print(f'Error in find_reading {err}')
            rslt = {}
        except Exception as err:
            print(f'Unexpected Error: {err}')
            rslt = {}
        return rslt


    def ami_meter_list(self) -> [dict]:
        ami_code = os.getenv('AMI_CODE', 'AMI')
        lst = []
        try:
            wmisdb = WMISDB()
            conn = wmisdb.connection
            cursor = conn.cursor()
            sql_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'list_ami_meters.sql')
            with open(sql_file, 'r') as file:
                cmd = file.read()
            cmd = cmd.replace('{ami_code}', ami_code)
            cursor.execute(cmd)
            rows = cursor.fetchall()
            if len(rows) > 0:
                for row in rows:
                    item = {
                        "meter_id": row[0],
                        "reading_date": row[1],
                        "odometer": row[2],
                        "description": row[3],
                        "lateral": row[4],
                    }
                    lst.append(item)
            wmisdb = None
        except DBError as err:
            print(f'Error in find_reading {err}')
        except Exception as err:
            print(f'Unexpected Error: {err}')
        return lst


