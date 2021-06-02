import pymongo
from bson.objectid import ObjectId

_mongo_client = None


def init_database(user, password):
    global _mongo_client

    # URL de la base de datos en Mongo Atlas
    url_db = f'mongodb+srv://{user}:{password}@bonobocluster.dl8wg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
    _mongo_client = pymongo.MongoClient(url_db)


def send_log(log):
    if _mongo_client is None:
        print('Mongo client is not initialized')
        return

    return _mongo_client.BonoboDB.logs.insert_one(log)


def send_transaction(transaction):
    if _mongo_client is None:
        print('Mongo client is not initialized')
        return

    return _mongo_client.BonoboDB.transacciones.insert_one(transaction)


def get_transaction_by_id(string_id):
    if _mongo_client is None:
        print('Mongo client is not initialized')
        return
    
    transacciones = _mongo_client.BonoboDB.transacciones
    data = transacciones.find_one({
        '_id': ObjectId(string_id)
    })

    if data == None:
        return {}

    return data

def close_client():
    if _mongo_client is None:
        print('Mongo client is not initialized')
        return

    _mongo_client.close()
    print('Mongo Client Closed')
