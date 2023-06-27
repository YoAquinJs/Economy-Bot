"""Este modulo contiene funcionalidades generales de la gestion de la economia de cada servidor de discord"""

from typing import Mapping

from database import db_utils
from database.db_utils import CollectionNames
from utils.utils import get_global_settings

_forge: Mapping[str, bool] = {}
_global_settings = get_global_settings()

def forge_coins(database_name) -> bool:
    """Inicia el forjado de monedas

    Args:
        database_name (str): Nombre de la base de datos del servidor de discord

    Returns:
        bool: Estado del forjado del servidor
    """
    
    global _forge

    if not database_name in _forge:
        _forge[database_name] = True

    return _forge[database_name]


def stop_forge_coins(database_name: str):
    """Detiene el forjado de monedas

    Args:
        database_name (str): Nombre de la base de datos del servidor de discord
    """
    
    global _forge
    _forge[database_name] = False


def reset_economy(database_name: str):
    """Pone las cuentas de todos los usuarios en 0.0

    Args:
        database_name (str): Nombre de la base de datos del servidor de discord
    """
    
    deregisters = db_utils.query_all(database_name, CollectionNames.deregisters.value)
    for deregister in deregisters.find({}):
        db_utils.modify("_id", deregister["_id"], "final_balance", _global_settings.initial_number_of_coins, database_name, CollectionNames.deregisters.value)#to new transfer
    
    users = db_utils.query_all(database_name, CollectionNames.users.value)
    for user in users.find({}):
        db_utils.modify("_id", user['_id'], "balance", _global_settings.initial_number_of_coins, database_name, CollectionNames.users.value)#to new transfer
