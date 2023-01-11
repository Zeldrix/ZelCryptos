#!/usr/bin/python3

import configparser
import functions
import json
import os

script_path = (os.path.dirname(os.path.realpath(__file__)) + os.sep)

# Import des données du fichier de configuration
config = configparser.ConfigParser()
config.read(script_path + 'config/config.ini')

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
functions.fill_database(DBPATH, cryptocurrencies_saved_data)
functions.debug_print(DEBUG, json.dumps(cryptocurrencies_saved_data, indent=2))