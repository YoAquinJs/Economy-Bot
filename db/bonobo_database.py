"""El módulo bonobo_database se encarga de las utilidades y la conexión con la base de datos de mongoDB"""

import discord
import pymongo
from bson.objectid import ObjectId

from utils.utils import get_global_settings

_mongo_client = None


def get_mongo_client() -> pymongo.MongoClient:
    """Esta función retorna un singleton de pymongo.MongoClient

        Returns:
                pymongo.MongoClient: Cliente para conectarse a una base de datos de MongoDB
    """

    if _mongo_client == None:
        global_settings = get_global_settings()
        init_database(
            global_settings['mongoUser'],
            global_settings['mongoPassword'])

    return _mongo_client


def init_database(user: str, password: str):
    """Inicializa el Cliente de la base de datos en el BonoboCluster de MongoDB

        Args:
                user (str): Usuario del Cluster de MongoDB
                password (str): Contraseña del usuario del Cluster de MongoDB
    """

    global _mongo_client

    # URL de la base de datos en Mongo Atlas
    url_db = f'mongodb+srv://{user}:{password}@bonobocluster.dl8wg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
    _mongo_client = pymongo.MongoClient(url_db)


def send_log(log: dict, guild: discord.Guild):
    """Envía un log a la base de datos Mongo

        Args:
                log (dict): Diccionario con los datos de un log
                guild (discord.Guild): Es la información de una Guild de discord

        Returns:
                pymongo.results.InsertOneResult: Contiene la información de la inserción en MongoDB
    """

    database_name = get_database_name(guild)

    return _mongo_client[database_name].logs.insert_one(log)


def send_transaction(transaction: dict, guild: discord.Guild):
    """Envia los datos de una transacción a la base de datos Mongo

    Args:
        transaction (dict): Diccionario con los datos de una transacción
        guild (discord.Guild): Es la información de una Guild de discord

    Returns:
        pymongo.results.InsertOneResult: Contiene la información de la inserción en MongoDB
    """

    database_name = get_database_name(guild)

    return _mongo_client[database_name].transacciones.insert_one(transaction)


def get_transaction_by_id(string_id: str, guild: discord.Guild):
    """Obtiene una transacción por id

        Args:
                string_id (str): id de la transacción
                guild (discord.Guild): Es la información de una Guild de discord

        Returns:
                dict: Es un diccionario con la transacción o None si no la encuentra
    """

    database_name = get_database_name(guild)

    transacciones = _mongo_client[database_name].transacciones
    data = transacciones.find_one({
        '_id': ObjectId(string_id)
    })

    return data


def close_client():
    """Desconecta el cliente de MongoDB
    """

    _mongo_client.close()
    print('Mongo Client Closed')


def get_random_user(guild: discord.Guild):
    """Obtiene un usuario al azar perteneciente a la guild

        Args:
                guild (discord.Guild): Es la información de una Guild de discord

        Returns:
                dict: Diccionario con el usuario
    """

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


def get_database_name(guild: discord.Guild) -> str:
    """Esta función genera el nombre de la base de datos de una guild de discord

        Args:
                guild (discord.Guild): Es la información de una Guild de discord

        Returns:
                str: Nombre único de la base de datos para el server de discord
    """

    name = guild.name
    if len(name) > 20:
        # Esta comprobacion se hace porque mongo no acepta nombres de base de datos mayor a 64 caracteres
        name = name.replace("a", "")
        name = name.replace("e", "")
        name = name.replace("i", "")
        name = name.replace("o", "")
        name = name.replace("u", "")

        if len(name) > 20:
            name = name[:20]

    return f'{name.replace(" ", "_")}_{guild.id}'
