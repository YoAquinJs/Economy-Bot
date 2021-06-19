import discord
import pymongo
from bson.objectid import ObjectId

from utils.utils import get_global_settings

_mongo_client = None


def get_mongo_client() -> pymongo.MongoClient:

    if _mongo_client == None:
        global_settings = get_global_settings()
        init_database(
            global_settings['mongoUser'], 
            global_settings['mongoPassword'])
        

    return _mongo_client


def init_database(user: str, password: str):
    global _mongo_client

    # URL de la base de datos en Mongo Atlas
    url_db = f'mongodb+srv://{user}:{password}@bonobocluster.dl8wg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
    _mongo_client = pymongo.MongoClient(url_db)


def send_log(log, guild: discord.Guild):
    database_name = get_database_name(guild)

    return _mongo_client[database_name].logs.insert_one(log)


def send_transaction(transaction, guild: discord.Guild):
    database_name = get_database_name(guild)

    return _mongo_client[database_name].transacciones.insert_one(transaction)


def get_transaction_by_id(string_id, guild: discord.Guild):
    database_name = get_database_name(guild)

    transacciones = _mongo_client[database_name].transacciones
    data = transacciones.find_one({
        '_id': ObjectId(string_id)
    })

    return data


def close_client():
    _mongo_client.close()
    print('Mongo Client Closed')


def get_random_user(guild: discord.Guild):
    database_name = get_database_name(guild)
    random_user = None

    collection = _mongo_client[database_name].balances
    cursor = collection.aggregate([
        {"$match": {"start_time": {"$exists": False}}},
        {"$sample": {"size": 1}}
    ])
    for i in cursor:
        random_user = i

    return random_user


def get_database_name(guild: discord.Guild):
    name = guild.name
    if len(name) > 20:
        # Esta comprobacion se hace porque mongo no acepta nombres de base de datos de las de 38 caracteres
        name = name.replace("a", "")
        name = name.replace("e", "")
        name = name.replace("i", "")
        name = name.replace("o", "")
        name = name.replace("u", "")

        if len(name) > 20:
            name = name[:20]

    return f'{name.replace(" ", "_")}_{guild.id}'
