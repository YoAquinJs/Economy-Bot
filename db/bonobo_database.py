import pymongo
from bson.objectid import ObjectId

_mongo_client = None
_database_name = ''

def init_database(user, password, guild_id):
    global _mongo_client, _database_name

    # URL de la base de datos en Mongo Atlas
    url_db = f'mongodb+srv://{user}:{password}@bonobocluster.dl8wg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
    _mongo_client = pymongo.MongoClient(url_db)
    _database_name = f'BonoboDB_{guild_id}'


def send_log(log):
    if _mongo_client is None:
        print('Mongo client is not initialized')
        return

    return _mongo_client[_database_name].logs.insert_one(log)


def send_transaction(transaction):
    if _mongo_client is None:
        print('Mongo client is not initialized')
        return

    return _mongo_client[_database_name].transacciones.insert_one(transaction)


def get_transaction_by_id(string_id):
    if _mongo_client is None:
        print('Mongo client is not initialized')
        return
    
    transacciones = _mongo_client[_database_name].transacciones
    data = transacciones.find_one({
        '_id': ObjectId(string_id)
    })

    return data

def close_client():
    if _mongo_client is None:
        print('Mongo client is not initialized')
        return

    _mongo_client.close()
    print('Mongo Client Closed')

def get_balance(user_id):
    collection = _mongo_client[_database_name].balances
    balance = collection.find_one({
        'user_id': user_id
    })

    return balance

def set_balance(user_id, ammount):
    balance = {
        'user_id': user_id,
        'ammount': ammount
    }

    collection = _mongo_client[_database_name].balances
    return collection.insert_one(balance)

def modify_balance(user_id, ammount):
    collection = _mongo_client[_database_name].balances
    query = {
        'user_id': user_id
    }
    
    new_balance = {"$set": {
        'user_id': user_id,
        'ammount': ammount
        }
    }

    
    return collection.update_one(query, new_balance)
    