"""Este modulo se encarga de funcionalidades de comandos en torno a usuarios"""

import bson
from typing import List
from random import choice

from models.economy_user import EconomyUser
from models.enums import CollectionNames
from database.db_utils import query_all

def get_users_starting_with(search: str, database_name: str) -> List[EconomyUser]:
    """Busqueda de todos los usuarios registrados 

    Args:
        search (str): Busqueda a realizar
        database_name (str): Nombre de la base de datos del servidor de discord

    Returns:
        List[EconomyUser]: Lista de todos los usuarios que tengan contengan la busqueda en su nombre
    """
    
    coll = query_all(database_name, CollectionNames.users.value)

    users = []
    results = coll.find({
        'name': {'$regex': f'^{search}', '$options' :'i'}
    })

    for result in results:
        user = EconomyUser(None, database_name=database_name)
        user.get_data_from_dict(result)

        users.append(user)

    return users


def get_random_user(_users: List[bson.ObjectId], database_name: str) -> EconomyUser:
    """Obtiene un usuario aleatorio de una lista de usuarios

        Args:
        _users (List[bson.ObjectId]): Lista de ids para escoger
        database_name (str): Nombre de la base de datos del servidor de discord
        Returns:
            EconomyUser: usuario aleatoriamente extraido
    """
    
    if len(_users) == 0:
        return EconomyUser.get_system_user()

    rnd_user = EconomyUser(choice(_users), database_name)
    exists = rnd_user.get_data_from_db()

    return rnd_user if exists is True else EconomyUser.get_system_user()
