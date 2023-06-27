"""Este modulo se encarga de gestionar la creacion de un nuevo log de transaccion"""

import bson
from typing import Union

from utils.utils import get_global_settings, get_time, to_object_id
from models.economy_user import EconomyUser
from models.logs import *
from models.enums import TransactionStatus, TransactionType


def new_transaction(sender: EconomyUser, receptor: EconomyUser, quantity: float, database_name: str, type: TransactionType) -> Union[TransactionStatus, bson.ObjectId]:
    """Hace una transaccion entre usuarios

    Args:
        sender (EconomyUser): Usuario que envia la transaccion
        receptor (EconomyUser): Usuario que recive la transaccion
        quantity (float): Monto de la transaccion
        data_base_name (str): nombre de la base de datos de mongo
        type (TransactionType): Tipo de transaccion

    Returns:
        Union[TransactionStatus, bson.ObjectId]: [Status de la transaccion, Id de la transaccion]
    """
    
    if type == TransactionType.initial_coins:
        sender = EconomyUser(to_object_id(0))
    else:
        global_settings = get_global_settings()
        quantity = round(quantity, global_settings.max_decimals)

        if quantity <= 0.0:
            return TransactionStatus.negative_quantity, ''
        if sender._id == receptor._id:
            return TransactionStatus.sender_is_receptor, ''

        receptor_exists = receptor.get_data_from_db()
        sender_exists = sender.get_data_from_db()

        if not sender_exists:
            return TransactionStatus.sender_not_exists, ''
        if not receptor_exists:
            return TransactionStatus.receptor_not_exists_not_exists, ''

        if sender.balance.value < quantity:
            return TransactionStatus.insufficient_coins, ''

        # Se hace la transacción
        sender.balance -= quantity

    receptor.balance += quantity
    
    # Se hace el log de la transaccion
    transaction_log = TransactionLog(get_time(), type, sender, receptor, quantity)
    transaccion_id = transaction_log.send_log_to_db(database_name).inserted_id

    return TransactionStatus.succesful, transaccion_id
