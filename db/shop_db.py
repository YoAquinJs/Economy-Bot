import discord
from db.bonobo_database import get_mongo_client, get_database_name

_mongo_client = get_mongo_client()


def save_product(product, guild: discord.Guild):
    database_name = get_database_name(guild)
    collection = _mongo_client[database_name].shop

    return collection.insert_one(product)


# Esta funcion busca un producto en la base datos
# En caso de no encontrarlo regresa None
# Recibe el id del mensaje con el que el producto fue registrado
def find_product(message_id: int, guild: discord.Guild):
    database_name = get_database_name(guild)
    collection = _mongo_client[database_name].shop

    return collection.find_one({
        'msg_id': message_id
    })


def delete_product(message_id: int, guild: discord.Guild):
    database_name = get_database_name(guild)
    collection = _mongo_client[database_name].shop

    return collection.delete_one({
        'msg_id': message_id
    })


def new_sale(sale, guild: discord.Guild):
    database_name = get_database_name(guild)
    if _mongo_client is None:
        print('Mongo client is not initialized')
        return

    return _mongo_client[database_name].sales.insert_one(sale)
