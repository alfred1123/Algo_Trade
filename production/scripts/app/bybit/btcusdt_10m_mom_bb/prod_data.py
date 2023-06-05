#!/usr/bin/python3

import requests
import time
import pandas as pd
import datetime
import logging
import os
import sys
from pprint import pprint
from dotenv import load_dotenv

home_dir = os.environ.get('TRADE_HOME_DIR')

sys.path.append(home_dir + '/production/scripts')
from utils import ThreadSafeFileWriter

log_location = home_dir + '/production/logs/' + datetime.datetime.now().strftime('%Y%m')+'.log'
data_location = r'data.csv'

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

load_dotenv()
glassnode_api_key = os.getenv('GLASSNODE_API_KEY')

symbol = 'BTC'
resolution = '10m' # 1month, 1w, 24h, 1h, 10m

### get data ###
while True:

    try:
        # if datetime.datetime.now().hour == 8 and datetime.datetime.now().minute == 0:
        if datetime.datetime.now().second == 0:

            ### timestamp adjustment ###
            until_unix_time = int(datetime.datetime.timestamp(datetime.datetime.now()))
            since_unix_time = until_unix_time - 100 * 600  # 1000m
            # unix_time = unix_time - 100*(60*60*1000) # 100h
            # unix_time = unix_time - 100*(24*60*60) # 1d
            # since_unix_time = until_unix_time - 100*(24*60*60) # 100d

            res = requests.get("https://api.glassnode.com/v1/metrics/market/price_usd_close",
                            params={"a": symbol , "s": since_unix_time, "u": until_unix_time, "api_key": glassnode_api_key, "i": resolution})
            df_new = pd.read_json(res.text)
            df_new.rename(columns={'t':'datetime', 'v':'close'}, inplace=True)
            df_new['datetime'] = df_new['datetime'] * 1000
            
            try:
                df_old = pd.read_csv(data_location)
                df_new = pd.concat([df_old, df_new]).drop_duplicates(subset=['datetime']).reset_index(drop=True)
            except:
                pass

            df_new = df_new[['datetime', 'close']]
            
            df_new.to_csv(data_location)
    except Exception as Argument:
        with ThreadSafeFileWriter(log_location) as f:
            f.write_data(str(datetime.datetime.now()) + ' ' + str(Argument) + '\n')
                  
    time.sleep(30)
