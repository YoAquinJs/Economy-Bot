import re
import pymongo
from bson.objectid import ObjectId

CLIENT_MONGO = None

def init_database(user, password):
    global CLIENT_MONGO

    # URL de la base de datos en Mongo Atlas
    url_db = f'mongodb+srv://{user}:{password}@bonobocluster.dl8wg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
    CLIENT_MONGO = pymongo.MongoClient(url_db)

def send_log(log):
    if CLIENT_MONGO == None:
        return

    collection_db = CLIENT_MONGO.BonoboDB.logs
    collection_db.insert_one(log)


def send_transaction(transaction):
    if CLIENT_MONGO == None:
        return
    
    collection_db = CLIENT_MONGO.BonoboDB.transacciones
    collection_db.insert_one(transaction)

def get_transaction_by_id(string_id):
    transacciones = CLIENT_MONGO.BonoboDB.transacciones
    data = transacciones.find_one({
        '_id': ObjectId(string_id)
    })

    if data == None:
        return {}

    return data