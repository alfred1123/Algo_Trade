#!/usr/bin/python3

'''
To do:
1. record bet_size of strategy for multiple strategy execution in future
3. telegram message precise and /n
5. build booking system for equity curve equation and continuously check execution
6. OOP installation for trade scripts
'''

import ccxt
import requests
import time
import pandas as pd
import numpy as np
import datetime
import os
from dotenv import load_dotenv
from pprint import pprint

home_dir = os.environ.get('TRADE_HOME_DIR')

sys.path.append(home_dir + '/production/scripts')
from utils import ThreadSafeFileWriter

log_location = home_dir + '/production/logs/' + datetime.datetime.now().strftime('%Y%m')+'.log'


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

load_dotenv()
exchange = ccxt.bybit({
    'apiKey': os.getenv('BYBIT_API_KEY'),
    'secret': os.getenv('BYBIT_SECRET_KEY'),
})

markets = exchange.load_markets()
# print(markets)
# print('********************************')
symbol = 'BTCUSDT'
market = exchange.market(symbol)
# print(market)

telegram_bot = os.getenv('TELEGRAM_BOT')

### signal ###
def signal(df, x, y):

    df['ma'] = df['close'].rolling(x).mean()
    df['sd'] = df['close'].rolling(x).std()
    df['z'] = (df['close'] - df['ma']) / df['sd']

    df['pos'] = np.where(df['z'] > y, 1, np.where(df['z'] < -y, -1, 0))

    pos = df['pos'].iloc[-1]

    df['dt'] = pd.to_datetime(df['datetime']/1000, unit='s')
    
    requests.get(telegram_bot +'z-score: '+ str(df.tail(1)['z']))
    # print(df.tail(10))

    return pos

### trade ###
def trade(pos):

    ### get account info before trade ###
    
    long = float(exchange.fetchPositions([symbol])[0]['info']['size'])
    short = float(exchange.fetchPositions([symbol])[1]['info']['size'])
    net_pos = long - short
    requests.get(telegram_bot + 'position: ' + str(net_pos))

    ### trade ###
    if pos == 1:
        if net_pos == 0:
            # print('long btc ' + str(bet_size))
            requests.get(telegram_bot+str(datetime.datetime.now())+' long btc ' + str(bet_size))
            order = exchange.create_order('BTCUSDT', 'market', 'buy', bet_size, None)
            # pprint(order)
        if net_pos == -bet_size:
            # print('long btc ' + str(bet_size*2))
            requests.get(telegram_bot+str(datetime.datetime.now())+' long btc '+str(bet_size*2))
            order = exchange.create_order('BTCUSDT', 'market', 'buy', bet_size, None, param={'reduce_only':True})
            order = exchange.create_order('BTCUSDT', 'market', 'buy', bet_size, None)
            # pprint(order)

    elif pos == 0:
        if net_pos == bet_size:
            # print('sell btc '+ str(bet_size))
            requests.get(telegram_bot+str(datetime.datetime.now())+' sell btc '+str(bet_size))
            order = exchange.create_order('BTCUSDT', 'market', 'sell', bet_size, None, param={'reduce_only':True})
            # pprint(order)
        if net_pos == -bet_size:
            # print('long btc '+ str(bet_size))
            requests.get(telegram_bot+str(datetime.datetime.now())+' long btc '+str(bet_size))
            order = exchange.create_order('BTCUSDT', 'market', 'buy', bet_size, None, param={'reduce_only':True})
            # pprint(order)
            
    elif pos == -1:
        if net_pos == bet_size:
            # print('sell btc ' + str(bet_size*2))
            requests.get(telegram_bot+str(datetime.datetime.now())+' sell btc '+str(bet_size*2))
            order = exchange.create_order('BTCUSDT', 'market', 'sell', bet_size, None, params={'reduce_only': True})
            order = exchange.create_order('BTCUSDT', 'market', 'sell', bet_size, None)
            # pprint(order)
        if net_pos == 0:
            # print('sell btc '+ str(bet_size))
            requests.get(telegram_bot+str(datetime.datetime.now())+' sell btc '+str(bet_size))
            order = exchange.create_order('BTCUSDT', 'market', 'sell', bet_size, None)
            # pprint(order)        

    time.sleep(1)

    ### get account info after trade ###
    long = float(exchange.fetchPositions([symbol])[0]['info']['size'])
    short = float(exchange.fetchPositions([symbol])[1]['info']['size'])
    net_pos = long - short
    
    # print('after signal')
    requests.get(telegram_bot+'after signal')
    # print('nav', datetime.datetime.now(), exchange.fetch_balance()['USDT']['total'])
    requests.get(telegram_bot+str(datetime.datetime.now())+' nav '+str(exchange.fetch_balance()['USDT']['total']))
### param ###
x = 11000
y = 0.5
pos = 0
bet_size = 0.03

while True:
    try:
        if datetime.datetime.now().second == 5:

            df = pd.read_csv(r'data.csv',engine = 'python')

            pos = signal(df, x, y)
            requests.get(telegram_bot+'btc position: '+ str(pos))

            trade(pos)
    except Exception as Argument:
        with ThreadSafeFileWriter(log_location) as f:
            f.write_data(str(datetime.datetime.now()) + ' ' + str(Argument) + '\n')

            time.sleep(15)




