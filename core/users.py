"""Este modulo se encarga de funcionalidades de comandos en torno a usuarios"""

from typing import List

from models.economy_user import EconomyUser
from models.enums import CollectionNames
from database.db_utils import query_all


def get_users_starting_with(search: str, database_name: str) -> List[EconomyUser]:
    """Busqueda de todos los usuarios registrados 

    Args:
        search (str): Busqueda a realizar
        database_name (str): Servidor de discord

    Returns:
        List[EconomyUser]: Lista de todos los usuarios que tengan contengan la busqueda en su nombre
    """
    
    coll = query_all(database_name, CollectionNames.users.value)

    users = []
    results = coll.find({
        'name': {'$regex': f'^{search}', '$options' :'i'}
    })

    for result in results:
        user = EconomyUser(-1, database_name=database_name)
        user.get_data_from_dict(result)

        users.append(user)

    return users


def get_random_user(database_name: str) -> EconomyUser:
    """Obtiene un usuario aleatorio en la base de datos de un servidor de discord

        Args:
                database_name (str): Nombre de la base de datos del servidor de discord

        Returns:
                EconomyUser: usuario aleatoriamente extraido
    """

    cursor = query_all(database_name, CollectionNames.users.value).aggregate([
        {"$match": {"start_time": {"$exists": False}}},
        {"$sample": {"size": 1}}
    ])

    rnd_data = None
    for i in cursor:
        rnd_data = i

    random_user = EconomyUser(rnd_data['_id'], database_name)
    random_user.get_data_from_dict(rnd_data)
    return random_user
