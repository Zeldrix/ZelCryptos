#!/usr/bin/python3

import os
from datetime import datetime, timedelta
import configparser
import sqlite3
from fastapi import FastAPI
import json

script_folder = (os.path.dirname(os.path.realpath(__file__)) + os.sep)
script_parent_folder = (os.path.abspath(os.path.join(script_folder, os.pardir)) + os.sep)

# Import des données du fichier de configuration
config = configparser.ConfigParser()
config.read(script_parent_folder + 'config/config.ini')

DBPATH = config['SQLite']['DBPath']
DEBUG = eval(config['Parameters']['Debug'])

app = FastAPI()

@app.get("/crypto/{token_symbol}/last")
def read_cryptos_last(token_symbol: str):
    timestamp = datetime.now().timestamp()
    error_code = 0
    error = ''
    output = {}

    try:
        with sqlite3.connect(DBPATH, check_same_thread=False) as con:
            cur = con.cursor()
            try:
                token = cur.execute(f'SELECT id, name, symbol FROM cryptocurrencies WHERE symbol = "{token_symbol.upper()}";').fetchone()
                try:
                    res = cur.execute(f'SELECT price, market_cap, cmc_rank, timestamp FROM last_data WHERE id = "{token[0]}";').fetchone()
                except:
                    error_code = 3
                    error = f'No data for {token[1]}'
            except:
                error_code = 2
                error = 'This cryptocurrency does not exists in our database'
    except:
        error_code = 1
        error = 'Database error'

    output_status = {
        'error_code': error_code,
        'timestamp': timestamp
    }
    
    if (0 == error_code):
        output_data = {
            'id' : token[0],
            'name' : token[1],
            'symbol' : token[2],
            'price' : res[0],
            'market_cap' : res[1],
            'cmc_rank' : res[2],
            'timestamp' : res[3]
        }
        output['data'] = output_data
    else:
        output_status['error_message'] = error

    output['status'] = output_status
    return output



@app.get("/crypto/{token_symbol}/history")
def read_cryptos_history(token_symbol: str, days_range: int = 7):
    timestamp = datetime.now().timestamp()
    error_code = 0
    error = ''
    output = {}

    try:
        with sqlite3.connect(DBPATH, check_same_thread=False) as con:
            cur = con.cursor()
            try:
                token = cur.execute(f'SELECT id, name, symbol FROM cryptocurrencies WHERE symbol = "{token_symbol.upper()}";').fetchone()
                try:
                    now = cur.execute(f'SELECT price, market_cap, cmc_rank, timestamp FROM last_data WHERE id = "{token[0]}";').fetchone()
                    history = fomrat_datas(history_get_data(cur, token[0], days_range, timestamp))
                except:
                    error_code = 3
                    error = f'No data for {token[1]}'
            except:
                error_code = 2
                error = 'This cryptocurrency does not exists in our database'
    except:
        error_code = 1
        error = 'Database error'

    output_status = {
        'error_code': error_code,
        'timestamp': datetime.now().timestamp()
    }
    
    if (0 == error_code):
        output_data = {
            'id' : token[0],
            'name' : token[1],
            'symbol' : token[2],
            'price' : now[0],
            'market_cap' : now[1],
            'cmc_rank' : now[2],
            'timestamp' : now[3],
            'history' : history
        }
        output['data'] = output_data
    else:
        output_status['error_message'] = error

    output['status'] = output_status
    return output

    


def history_get_data(cur: sqlite3.Cursor, token_id: int, days_range: int, timestamp: datetime.date) -> list:
    range_timestamp = datetime.timestamp(datetime.combine(datetime.fromtimestamp(timestamp).date() - timedelta(days=days_range), datetime.min.time()))
    datas = cur.execute(f'SELECT timestamp, price, market_cap from data WHERE id = "{token_id}" AND timestamp > {range_timestamp} ORDER BY timestamp DESC;').fetchall()
    return datas

def fomrat_datas(datas: list) -> dict:
    output = {}
    for data in datas:
        output[data[0]] = {
            'price': data[1],
            'market_cap': data[2]
        }
    return output