"""Este modulo contiene funcionalidades generales de la gestion de la economia de cada servidor de discord"""

import bson
from typing import Mapping, List

from database import db_utils
from database.db_utils import CollectionNames
from utils.utils import get_global_settings

_frozen = False
_forge: Mapping[str, bool] = {}
_users: Mapping[str, List[bson.ObjectId]] = {}

_global_settings = get_global_settings()


def forge_coins_status(database_name: str, status: bool):
    """Inicia el forjado de monedas

    Args:
        database_name (str): Nombre de la base de datos del servidor de discord
        status (bool): Estado del forjado, verdadero para iniciar, falso para detener
    Returns:
        bool: Estado del forjado del servidor
    """
    
    global _forge

    _forge[database_name] = status


def is_forging(database_name: str) -> bool:
    """Detiene el forjado de monedas

    Args:
        database_name (str): Nombre de la base de datos del servidor de discord
    """
    
    global _forge
    return _forge[database_name] if database_name in _forge.keys() else False


def reset_economy(database_name: str):
    """Pone las cuentas de todos los usuarios en 0.0

    Args:
        database_name (str): Nombre de la base de datos del servidor de discord
    """
    
    global _frozen
    _frozen = True
    deregisters = db_utils.query_all(database_name, CollectionNames.deregisters.value)
    for deregister in deregisters.find({}):
        db_utils.modify("_id", deregister["_id"], "final_balance", _global_settings.initial_number_of_coins, database_name, CollectionNames.deregisters.value)#to new transfer
    
    users = db_utils.query_all(database_name, CollectionNames.users.value)
    for user in users.find({}):
        db_utils.modify("_id", user['_id'], "balance", _global_settings.initial_number_of_coins, database_name, CollectionNames.users.value)#to new transfer
        
    _frozen = False


def update_user_status(_id: bson.ObjectId, database_name: str):
    """Inserta o remueve un usuario al registrarse o desregistrarse

    Args:
        _id (bson.ObjectId): Id del usuario
        database_name (str): Nombre de la base de datos del servidor de discord
    """
    
    global _users
    
    if database_name not in _users.keys():
        _users[database_name] = []
    
    _users[database_name].remove(_id) if _id in _users[database_name] else _users[database_name].append(_id)
    
    
def get_users(database_name: str) -> List[int]:
    """Obtiene la lista de usuarios actual

    Args:
        database_name (str): Nombre de la base de datos del servidor de discord

    Returns:
        List[int]: Lista de los ids de los usuarios al momento
    """
    
    return _users[database_name]