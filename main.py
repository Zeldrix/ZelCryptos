#!/usr/bin/python3

import configparser
import functions
import json

# Import des données du fichier de configuration
config = configparser.ConfigParser()
config.read('config/config.ini')

DBPATH = config['SQLite']['DBPath']
API_KEY = config['CoinMarketCap']['API_KEY']
CRYPTOSLIST = config['Parameters']['CryptosList']
DEBUG = eval(config['Parameters']['Debug'])

# Initialisation de la DB
functions.init_database(DBPATH)

# Initialisation de la requète API
request_url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
request_querystring = {"symbol":CRYPTOSLIST}
request_headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": API_KEY}

# Liste des données à récupérer pour chaque crypto
dataToStore = ['id', 'name', 'cmc_rank', 'last_updated', ['quote','USD','price'], ['quote','USD','market_cap']]


########################################  DEBUT DU PROGRAMME  ########################################

cryptocurrencies_saved_data = functions.get_and_sort_cryptodata(request_url, request_headers, request_querystring, dataToStore)

for cryptocurrency in cryptocurrencies_saved_data:
    current_crypto = cryptocurrencies_saved_data[cryptocurrency]
    if (False == functions.did_crypto_exists(DBPATH, current_crypto['id'])):
        functions.insert_in_table_crypto(DBPATH, current_crypto['id'], current_crypto['name'], cryptocurrency)
    functions.insert_in_table_data(DBPATH, current_crypto['id'], current_crypto['last_updated'], current_crypto['cmc_rank'], current_crypto['price'], current_crypto['market_cap'])


functions.debug_print(DEBUG, json.dumps(cryptocurrencies_saved_data, indent=2))