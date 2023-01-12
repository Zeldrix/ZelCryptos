#!/usr/bin/python3

import requests
import json
import sqlite3
from datetime import datetime

def debug_print(debug: bool, string: str) -> None:
    if debug:
        print(string)


def request_cryptodata(url: str, headers: str, querystring: str) -> dict:
    response = requests.request("GET", url, headers=headers, params=querystring)
    response_json = json.loads(response.text)
    if (0 != response_json["status"]["error_code"]) :
        return 'Error ' + str(response_json["status"]["error_code"]) + ' : ' + str(response_json["status"]["error_message"])
    else : # Récupération seulement des données qu'on va utiliser
        return response_json['data']

def sort_cryptodata(request_data: dict, data_to_store: list) -> dict:
    cryptocurrencies_saved_data = {}
    for cryptocurrency in request_data:
        saved_data = {}
        cryptocurrency_data = request_data[cryptocurrency][0]
        for data in data_to_store:
            if (isinstance(data, list)): # Si il s'agit d'une liste (ce qui induit qu'on rentre dans quote/USD)
                saved_data[data[2]] = cryptocurrency_data[data[0]][data[1]][data[2]]
            else :
                saved_data[data] = cryptocurrency_data[data]
        cryptocurrencies_saved_data[cryptocurrency] = saved_data # On sauvegarde notre travaille dans le dictionnaire au nom de la crypto
    return cryptocurrencies_saved_data

def get_and_sort_cryptodata(url: str, headers: str, querystring: str, data_to_store: list) -> dict:
    cryptocurrencies_data = request_cryptodata(url, headers, querystring)
    if (isinstance(cryptocurrencies_data, str)):
        print(cryptocurrencies_data)
        exit()
    cryptocurrencies_saved_data = sort_cryptodata(cryptocurrencies_data, data_to_store)
    return cryptocurrencies_saved_data

def fill_database(DBPath: str, cryptocurrencies_sorted_data: dict, timestamp: float) -> None:
    for cryptocurrency in cryptocurrencies_sorted_data:
        current_crypto = cryptocurrencies_sorted_data[cryptocurrency]
        if (False == did_crypto_exists(DBPath, current_crypto['id'])):
            insert_in_table_crypto(DBPath, current_crypto['id'], current_crypto['name'], cryptocurrency)
        insert_in_table_data(DBPath, current_crypto['id'], timestamp, current_crypto['cmc_rank'], current_crypto['price'], current_crypto['market_cap'])


def open_database(DBPath: str) -> dict:
    sqlite_connnect = sqlite3.connect(DBPath)
    sqlite_cursor = sqlite_connnect.cursor()
    return {'connect': sqlite_connnect, 'cursor': sqlite_cursor}

def close_database(connect: sqlite3.connect) -> None:
    connect.close()

def init_database(DBPath: str) -> None:
    db = open_database(DBPath)
    db['cursor'].execute('CREATE TABLE IF NOT EXISTS cryptocurrencies (id INT PRIMARY KEY, name TEXT, symbol TEXT);')
    db['cursor'].execute('CREATE TABLE IF NOT EXISTS data (id INT, timestamp REAL, cmc_rank INT, price REAL, market_cap REAL);')
    db['cursor'].execute('CREATE TABLE IF NOT EXISTS last_data (id INT PRIMARY KEY, timestamp REAL, cmc_rank INT, price REAL, market_cap REAL);')
    close_database(db['connect'])

def insert_in_table_crypto(DBPath: str, crypto_id: int, name: str, symbol: str) -> None:
    db = open_database(DBPath)
    db['cursor'].execute(f'INSERT INTO cryptocurrencies VALUES ("{crypto_id}", "{name}", "{symbol}");')
    db['connect'].commit()
    close_database(db['connect'])

def insert_in_table_data(DBPath: str, crypto_id: int, timestamp: str, cmc_rank: int, price: float, market_cap: float) -> None:
    db = open_database(DBPath)
    if (0 == datetime.fromtimestamp(timestamp).minute):
        db['cursor'].execute(f'INSERT INTO data VALUES ("{crypto_id}", "{timestamp}", "{cmc_rank}", "{price}", "{market_cap}");')
    db['cursor'].execute(f'DELETE FROM last_data WHERE id = "{crypto_id}";') # On supprime la dernière valeur pour la crypto pour la réinsérer ensuite
    db['cursor'].execute(f'INSERT INTO last_data VALUES ("{crypto_id}", "{timestamp}", "{cmc_rank}", "{price}", "{market_cap}");')
    db['connect'].commit()
    close_database(db['connect'])

def did_crypto_exists(DBPath: str, id: int) -> bool:
    db = open_database(DBPath)
    result = db['cursor'].execute(f'SELECT id FROM cryptocurrencies WHERE id = "{id}";').fetchone()
    if (None == result):
        return False
    result_id = result[0]
    close_database(db['connect'])
    if (id == result_id):
        return True
    return False