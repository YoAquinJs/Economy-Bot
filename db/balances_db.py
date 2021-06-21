"""El módulo balances_db hace gestión de los balances de los usuarios en la base de datos de MongoDB"""

import discord
from db.bonobo_database import get_mongo_client, get_database_name

_mongo_client = get_mongo_client()


def get_balance(user_id: int, guild: discord.Guild):
    """Esta función retorna un diccionario con el balance de un usuario o None si el usuario no existe

        Args:
                user_id (int): Es el ID del usuario en discord
                guild (discord.Guild): Es la información de una Guild de discord

        Returns:
                dict: Diccionario que contiene el balance del usuario o None si el usuario no existe
    """

    database_name = get_database_name(guild)

    collection = _mongo_client[database_name].balances
    balance = collection.find_one({
        'user_id': user_id
    })

    return balance


def create_balance(user_id: int, user_name, balance, guild: discord.Guild):
    """Esta función registra a un usuario de discord en la Bonobo Economy

        Args:
                user_id (int): Es el ID del usuario en discord
                user_name ([type]): Nombre del usuario en discord
                balance ([type]): Es el número inicial de monedas que va a tener el usuario al momento de registrarse
                guild (discord.Guild): Es la información de una Guild de discord

        Returns:
                pymongo.results.InsertOneResult: Contiene la información de la inserción en MongoDB
    """

    database_name = get_database_name(guild)

    balance = {
        'user_id': user_id,
        'user_name': user_name,
        'balance': balance
    }

    collection = _mongo_client[database_name].balances

    return collection.insert_one(balance)


def modify_balance(user_id: int, balance: int, guild: discord.Guild):
    """Modifica el balance de un usuario

        Args:
                user_id (int): Es el ID del usuario en discord
                balance (int): Es el nuevo balance
                guild (discord.Guild): Es la información de una Guild de discord

        Returns:
                pymongo.results.UpdateResult: Información sobre la actualización del documento en MongoDB
    """

    database_name = get_database_name(guild)

    collection = _mongo_client[database_name].balances
    query = {
        'user_id': user_id
    }

    new_balance = {"$set": {
        'balance': balance
    }
    }

    return collection.update_one(query, new_balance)


def get_balances_cursor(guild: discord.Guild):
    """Regresa un cursor de MongoDB con todos los balances de los usuarios registrados en la Bonobo Economy

        Args:
                guild (discord.Guild): Es la información de una Guild de discord

        Returns:
                pymongo.cursor.Cursor: Es una clase iterable sobre Mongo query results.
    """

    database_name = get_database_name(guild)
    collection = _mongo_client[database_name].balances

    return collection.find({})
