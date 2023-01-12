from datetime import datetime, timedelta

timestamp = 1673553240.0

print(datetime.timestamp(datetime.combine(datetime.fromtimestamp(timestamp).date() - timedelta(days=7), datetime.min.time())))


"""


retention = {
    'soft': {
        'days': 30,
        'dpd': 1 # dpd = Data per day - On garde 1 valeur / jour
    },
    'medium': {
        'days': 10,
        'dpd': 6 # dpd = Data per day - On garde 6 valeurs / jour
    }
}

for retention_plan in retention:
    retention_date = datetime.fromtimestamp(timestamp).date() - timedelta(days=retention[retention_plan])
    retention_timestamp = datetime.timestamp(retention_date)
    db = open_database(DBPath)
    ids = db['cursor'].execute('SELECT id from cryptocurrencies;').fetchall()
    for id in ids:
        timestamps = db['cursor'].execute(f'SELECT timestamp from cryptocurrencies WHERE id = "{id} AND timestamp < "{retention_timestamp}";').fetchall()
        for ts in timestamps:
            if (datetime.fromtimestamp(timestamp).date() == datetime.fromtimestamp(timestamp).date()):
                print('a continuer')
"""