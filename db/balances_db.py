import discord
from db.bonobo_database import get_mongo_client, get_database_name

_mongo_client = get_mongo_client()


def get_balance(user_id: int, guild: discord.Guild):
    database_name = get_database_name(guild)

    collection = _mongo_client[database_name].balances
    balance = collection.find_one({
        'user_id': user_id
    })

    return balance


def create_balance(user_id: int, user_name, balance, guild: discord.Guild):
    database_name = get_database_name(guild)

    balance = {
        'user_id': user_id,
        'user_name': user_name,
        'balance': balance
    }

    collection = _mongo_client[database_name].balances

    return collection.insert_one(balance)


def modify_balance(user_id: int, balance: int, guild: discord.Guild):
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
    database_name = get_database_name(guild)
    collection = _mongo_client[database_name].balances

    return collection.find({})
