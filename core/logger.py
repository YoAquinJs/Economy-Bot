"""Este modulo contiene utilidades de registro de logs"""

from bson import ObjectId
from typing import Tuple

from models.economy_user import EconomyUser
from models.logs import *

def send_unregistered_log(user: EconomyUser, motive: str):
    """Desregistro de un usuario en la base de datos de la economia y manda el log

    Args:
        user (EconomyUser): usuario
        motive (str): Motivo del desregistro
    """

    desregister_log = UnregisterLog(user.id, user.name, user.balance.value, motive)
    desregister_log.send_log_to_db(user.database_name)


def report_bug_log(user_id: int, title: str, description: str, command: str, database_name: str) -> Tuple[bool, ObjectId]:
    """Genera un log que reporta un bug a los desarrolladores

    Args:
        user_id (int): id del usuario que reporta el bug
        title (str): titulo del bug
        description (str): descripcion del bug
        command (str): comando que ocasiona el bug
        database_name (str): Nombre de la base de datos de mongo

    Returns:
        Tuple[bool, ObjectId]: [Si el trabajo fue exitoso, id registrado]
    """

    user = EconomyUser(user_id, database_name=database_name)
    exists_user = user.get_data_from_db()

    if exists_user:
        bug = BugLog(title, description, command)
        insert_result = bug.send_log_to_db(database_name)

        return True, insert_result.inserted_id
    else:
        return False, None