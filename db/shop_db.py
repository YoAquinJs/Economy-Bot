"""El módulo shop_db se encarga de guardar y gestionar los datos de la tienda del Economy Bot"""

import discord
from db.bonobo_database import get_mongo_client, get_database_name

_mongo_client = get_mongo_client()


def save_product(product, guild: discord.Guild):
    """Guarda un producto en la base de datos

        Args:
                product (dict): diccionario con la información de un producto
                guild (discord.Guild): Es la información de una Guild de discord

        Returns:
                pymongo.results.InsertOneResult: Contiene la información de la inserción en MongoDB
    """

    database_name = get_database_name(guild)
    collection = _mongo_client[database_name].shop

    return collection.insert_one(product)


def find_product(message_id: int, guild: discord.Guild):
    """Esta función busca un producto en la base datos y en caso de no encontrarlo regresa None

    Args:
        message_id (int): id del mensaje con el que el producto fue registrado
        guild (discord.Guild): Es la información de una Guild de discord

    Returns:
        dict: Producto
    """

    database_name = get_database_name(guild)
    collection = _mongo_client[database_name].shop

    return collection.find_one({
        'msg_id': message_id
    })


def delete_product(message_id: int, guild: discord.Guild):
    """Borra un producto en la base de datos

    Args:
        message_id (int): id del mensaje con el que el producto fue registrado
        guild (discord.Guild): Es la información de una Guild de discord

    Returns:
        pymongo.results.DeleteResult: Información del borrado en MongoDB
    """

    database_name = get_database_name(guild)
    collection = _mongo_client[database_name].shop

    return collection.delete_one({
        'msg_id': message_id
    })


def new_sale(sale, guild: discord.Guild):
    """Guarda la información de una venta en la base de datos

        Args:
                sale (dict): Diccionario con la información de la venta
                guild (discord.Guild): Es la información de una Guild de discord

        Returns:
                pymongo.results.InsertOneResult: Contiene la información de la inserción en MongoDB
    """

    database_name = get_database_name(guild)
    if _mongo_client is None:
        print('Mongo client is not initialized')
        return

    return _mongo_client[database_name].sales.insert_one(sale)
