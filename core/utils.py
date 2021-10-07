from typing import Tuple

from models.economy_user import EconomyUser
from models.logs import *

def send_unregistered_log(user: EconomyUser, database_name: str, motive: str):
    """Anula el registro de un usuario en la base de datos de la economia y manda el log

    Args:
        user (EconomyUser): usuario
        data_base_name (str): nombre de la base de datos de mongo
        motive (str): Motivo del desregistro
    """

    desregister_log = UnregisterLog(user.id, user.name, user.balance.value, motive)
    desregister_log.send_log_to_db(database_name)


def report_bug_log(user_id: int, description: str, command: str, database_name: str) -> Tuple[bool, BugLog]:
    """Genera un log que reporta un bug a los desarrolladores

    Args:
        user_id (int): id del usuario que reporta el bug
        title (str): titulo del bug
        description (str): descripcion del bug
        command (str): comando que ocasiona el bug
        database_name (str): Nombre de la base de datos de mongo

    Returns:
        Tuple[bool, BugLog]: [Si el trabajo fue exitoso, log]
    """

    user = EconomyUser(user_id, database_name=database_name)
    exists_user = user.user_exists()

    if exists_user:
        bug = BugLog(description, command)
        bug.send_log_to_db(database_name)

        return True, bug
    else:
        return False, None
