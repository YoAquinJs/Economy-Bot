from typing import Mapping

from database import db_utils
from database.db_utils import CollectionNames


_forge: Mapping[str, bool] = {}


def forge_coins(database_name):
    global _forge

    if not database_name in _forge:
        _forge[database_name] = True

    return _forge[database_name]


def stop_forge_coins(database_name: str):
    global _forge
    _forge[database_name] = False


def reset_economy(database_name: str):
    """Pone las cuentas de todos los usuarios en 0.0

    Args:
        database_name (str): Nombre de la base de datos de mongo
    """
    
    db_utils.delete_all(database_name, CollectionNames.deregisters.value)
    users = db_utils.query_all(database_name, CollectionNames.users.value)
    for user in users.find({}):
        db_utils.modify("_id", user['_id'], "balance",
                        0.0, database_name, CollectionNames.users.value)
