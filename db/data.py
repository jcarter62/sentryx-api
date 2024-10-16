import datetime
import os.path
import uuid
import json
from .wmisdb import WMISDB, DBError
from dotenv import load_dotenv
import os

load_dotenv()

class Data:
    def __init__(self):
        if not self.__table_ami_readings_exists__():
            self.__create_ami_readings__()
        if not self.__table_ami_data_exists__():
            self.__create_ami_data__()

    # table name: ami_readings, columns
    # meter_id, reading_date, reading_time, reading_value, reading_type, reading_status, reading_unit, reading_source

    def __table_ami_readings_exists__(self) -> bool:
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

    def __create_ami_readings__(self) -> bool:
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

    def __table_ami_data_exists__(self) -> bool:
        rslt = False
        try:
            wmisdb = WMISDB()
            conn = wmisdb.connection
            cursor = conn.cursor()
            cmd = 'select count(*) from information_schema.tables where table_name = \'ami_data\';'
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

    def __create_ami_data__(self) -> bool:
        rslt = False
        try:
            wmisdb = WMISDB()
            conn = wmisdb.connection
            cursor = conn.cursor()
            # open create_ami_readings.sql and read the contents into cmd
            sql_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'create_ami_data.sql')
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

    def insert_ami_data(self, meter_id: str, reading_date: str, reading: float, data: str) -> tuple[str, int, str]:
        rslt = False
        cmd = ''
        try:
            wmisdb = WMISDB()
            conn = wmisdb.connection
            cursor = conn.cursor()
            # calculate lowercase uuid
            new_id = str(uuid.uuid4()).lower().replace('-', '')
            # sanitize data
            # how do I convert data to a string?

            datastr = json.dumps(data)
            while chr(39) in datastr:
                datastr = datastr.replace(chr(39),chr(94))

            # determine if reading_date is a valid date
            try:
                __test_date__ = datetime.datetime.fromisoformat(reading_date)
            except Exception as err:
                reading_date = ''

            cmd = f'insert into ami_data (id, meter_id, reading_dt, reading, tstamp, data ) ' + \
                  f'values (\'{new_id}\', \'{meter_id}\', \'{reading_date}\', {reading}, ' + \
                  f'getdate(), \'{datastr}\');'

            wmisdb = None
            rslt = "Ok"
            code = 201
        except DBError as err:
            rslt = f'Error in insert_reading {err}'
            code = 500
        except Exception as err:
            rslt = f'Unexpected Error: {err}'
            code = 500

        return rslt, code, cmd


    def insert_reading(self, meter_id: str, reading_date: str, reading: float,
                       rd_type: str = '', rd_status: str = '', rd_unit: str = '', rd_source: str = ''
                       ) -> tuple[str, int, str]:
        rslt = ''
        cmd = ''
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
                cmd = ''
            else:
                cmd = f'insert into ami_readings (meter_id, reading_dt, reading, rd_type, rd_status, rd_unit, rd_source) ' + \
                      f'values (\'{meter_id}\', \'{reading_date}\', {reading}, ' + \
                      f' \'{rd_type}\', \'{rd_status}\', \'{rd_unit}\', \'{rd_source}\' );'

                wmisdb = None
                rslt = "Ok"
                code = 201
        except DBError as err:
            rslt = f'Error in insert_reading {err}'
            code = 500
        except Exception as err:
            rslt = f'Unexpected Error: {err}'
            code = 500
        return rslt, code, cmd

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

    def last_wmis_reading(self, meter_id:str )-> dict:
        rslt = {}
        try:
            wmisdb = WMISDB()
            conn = wmisdb.connection
            cursor = conn.cursor()
            cmd = f'select top 1 turnout_id as meter_id, reading, readingdate  from TRNDEMST where turnout_id = ? ' + \
                    'order by readingdate desc;'

            cursor.execute(cmd, (meter_id,))
            rows = cursor.fetchall()
            try:
                if len(rows) > 0:
                    row = rows[0]
                    rslt = {
                        'meter_id':row[0],
                        'reading':row[1],
                        'reading_date':row[2],
                    }
                else:
                    rslt = {}
            except Exception as err:
                rslt = {}
            finally:
                wmisdb = None
        except DBError as err:
            print(f'Error in find_reading {err}')
            rslt = {}
        except Exception as err:
            print(f'Unexpected Error: {err}')
            rslt = {}
        return rslt


    def sp_ami_readings(self, target_date:str = '')-> []:
        rslt = []
        try:
            wmisdb = WMISDB()
            conn = wmisdb.connection
            cursor = conn.cursor()
            if target_date <= '':
                cmd = 'exec sp_ami_readings;'
            else:
                cmd = f'exec sp_ami_readings @targetdate=\'{target_date}\';'

            cursor.execute(cmd)
            rows = cursor.fetchall()
            try:
                if len(rows) > 0:
                    for row in rows:
                        rslt.append({
                            'meter_id':row[0],
                            'readingdate':row[1],
                            'reading':row[2],
                            'readingstatus':row[3],
                            'daysold':row[4],
                            'rec_action':row[5],
                            'lastreadingdate':row[6],
                            'lastreading':row[7],
                        })
                else:
                    rslt = []
            except Exception as err:
                rslt = []
            finally:
                wmisdb = None
        except DBError as err:
            print(f'DB Error {err}')
        except Exception as err:
            print(f'Unexpected Error: {err}')
        return rslt
        # note: GRANT EXECUTE ON [dbo].[sp_ami_readings] TO [api]


    def post_reading(self, meter_id:str, reading_date:str, reading:str, operator:str)-> dict:
        rslt = {}
        try:
            wmisdb = WMISDB()
            conn = wmisdb.connection
            cursor = conn.cursor()

            chk_cmd = 'select isnull(count(*),0) from TabletIncomingMeterReadings51 ' + \
                     f'where (Meter_ID = \'{meter_id}\') and ' + \
                     f'(ReadingDate = \'{reading_date}\') and ' + \
                     f'(round(Odometer,2) = round({reading},2)); '

            cursor.execute(chk_cmd)
            rows = cursor.fetchall()
            nrows = 0
            if rows[0][0] > 0:
                nrows = rows[0][0]
            if nrows > 0:
                rslt = {'message':'Duplicate','code':208}
            else:
                versionstr = '51.2017'
                current_datetime = datetime.datetime.now().isoformat()

                cmd = 'insert into ' + \
                      '  TabletIncomingMeterReadings51( ' + \
                      '      [VersionString], [MeterType], [Meter_ID], [ReadingDate], ' + \
                      '      [TabletOperator], [Tablet_ID], [Time_Stamp], [Odometer], ' + \
                      '      [ObservedFlow], [Notes], [Geographic], [ReadingFileName]) ' + \
                      '  values( ' + \
                      f'      \'{versionstr}\', \'Turnout\', \'{meter_id}\', \'{reading_date}\', ' + \
                      f'      \'{operator}\', \'ami-ui\', getdate(), {reading}, ' + \
                      '      0, \'\', \'\', \'\'); '

                cursor.execute(cmd)
                conn.commit()

                wmisdb = None
                rslt = {'message':'Ok','code':200}
        except DBError as err:
            rslt = {'message':f'Error: {err}', 'code':500}
        except Exception as err:
            rslt = {'message':f'Error: {err}', 'code':500}
        return rslt
        #

    def process_readings(self)-> dict:
        rslt = {}
        try:
            wmisdb = WMISDB()
            conn = wmisdb.connection
            cursor = conn.cursor()

            cmd = 'exec sp_mi_process;'
            cursor.execute(cmd)
            conn.commit()

            wmisdb = None
            rslt = {'message':'Ok','code':200}
        except DBError as err:
            rslt = {'message':f'Error: {err}', 'code':500}
        except Exception as err:
            rslt = {'message':f'Error: {err}', 'code':500}
        return rslt
        #
