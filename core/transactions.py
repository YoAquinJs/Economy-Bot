from typing import Tuple

from utils.utils import get_global_settings, get_time
from models.economy_user import EconomyUser
from models.logs import *
from models.enums import TransactionStatus


def new_transaction(sender: EconomyUser, receptor: EconomyUser, quantity: float, database_name: str, channel_name: str, type: str = 'transferencia') -> Tuple[TransactionStatus, str]:
    """Hace una transaccion entre usuarios

    Args:
        sender (User): Usuario que envia la transaccion
        receiver (User): Usuario que recive la transaccion
        quantity (float): Monto de la transaccion
        data_base_name (str): nombre de la base de datos de mongo
        channel_name (str): Nombre del canal

    Returns:
        Tuple[str, str]: [status de la transaccion, id de la transaccion]
    """

    global_settings = get_global_settings()

    if quantity <= 0.0:
        return TransactionStatus.negative_quantity, ''
    if sender._id == receptor._id:
        return TransactionStatus.sender_is_receptor, ''

    receptor_exists = receptor.user_exists()
    sender_exists = sender.user_exists()

    if not sender_exists:
        return TransactionStatus.sender_not_exists, ''
    if not receptor_exists:
        return TransactionStatus.receptor_not_exists, ''

    if sender.balance.value < quantity:
        return TransactionStatus.insufficient_coins, ''

    # Se hace la transacción
    sender.balance -= quantity
    receptor.balance += quantity

    # # Se hace el log de la transaccion
    transaction_log = TransactionLog(
        get_time(), type, sender, receptor, quantity, channel_name)
    transaction_id = transaction_log.send_log_to_db(database_name).inserted_id

    return TransactionStatus.succesful, transaction_id
