import pymongo
from bson.objectid import ObjectId

_mongo_client = None


def init_database(user, password):
    global _mongo_client, _database_name

    # URL de la base de datos en Mongo Atlas
    url_db = f'mongodb+srv://{user}:{password}@bonobocluster.dl8wg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
    _mongo_client = pymongo.MongoClient(url_db)


def send_log(log, guild):
    database_name = _get_database_name(guild)

    if _mongo_client is None:
        print('Mongo client is not initialized')
        return

    return _mongo_client[database_name].logs.insert_one(log)


def send_transaction(transaction, guild):
    database_name = _get_database_name(guild)
    if _mongo_client is None:
        print('Mongo client is not initialized')
        return

    return _mongo_client[database_name].transacciones.insert_one(transaction)


def get_transaction_by_id(string_id, guild):
    database_name = _get_database_name(guild)

    if _mongo_client is None:
        print('Mongo client is not initialized')
        return
    
    transacciones = _mongo_client[database_name].transacciones
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


def get_balance(user_id: int, guild):
    database_name = _get_database_name(guild)

    collection = _mongo_client[database_name].balances
    balance = collection.find_one({
        'user_id': user_id
    })

    return balance


def create_balance(user_id: int, user_name, balance, guild):
    database_name = _get_database_name(guild)

    balance = {
        'user_id': user_id,
        'user_name': user_name,
        'balance': balance
    }

    collection = _mongo_client[database_name].balances

    return collection.insert_one(balance)


def modify_balance(user_id: int, balance: int, guild):
    database_name = _get_database_name(guild)

    collection = _mongo_client[database_name].balances
    query = {
        'user_id': user_id
    }
    
    new_balance = {"$set": {
        'balance': balance
        }
    }

    return collection.update_one(query, new_balance)


def _get_database_name(guild):
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


def get_random_user(guild):
    database_name = _get_database_name(guild)
    random_user = None

    collection = _mongo_client[database_name].balances
    cursor = collection.aggregate([
        { "$match": { "start_time": { "$exists": False } } },
        { "$sample": { "size": 1 } }
    ])
    for i in cursor:
        random_user = i

    return random_user


def get_balances_cursor(guild):
    database_name = _get_database_name(guild)
    collection = _mongo_client[database_name].balances
    
    return collection.find({})


def save_product(product, guild):
    database_name = _get_database_name(guild)
    collection = _mongo_client[database_name].shop

    return collection.insert_one(product)


# Esta funcion busca un producto en la base datos
# En caso de no encontrarlo regresa None
# Recibe el id del mensaje con el que el producto fue registrado
def find_product(message_id, guild):
    database_name = _get_database_name(guild)
    collection = _mongo_client[database_name].shop

    return collection.find_one({
        'msg_id': message_id
    })


def delete_product(message_id, guild):
    database_name = _get_database_name(guild)
    collection = _mongo_client[database_name].shop

    return collection.delete_one({
        'msg_id': message_id
    })


def new_sale(sale, guild):
    database_name = _get_database_name(guild)
    if _mongo_client is None:
        print('Mongo client is not initialized')
        return

    return _mongo_client[database_name].sales.insert_one(sale)
