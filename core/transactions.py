"""Este modulo se encarga de gestionar la creacion de un nuevo log de transaccion"""

import bson
from typing import Union

from utils.utils import get_global_settings, get_time, id_to_objectid
from models.economy_user import EconomyUser
from models.product import Product
from models.logs import *
from models.enums import TransactionStatus, TransactionType

_global_settings = get_global_settings()


def new_transaction(sender: EconomyUser, receptor: EconomyUser, quantity: float, database_name: str, type: TransactionType, 
                    reason: str = '', product: Product = None, admin: EconomyUser = None) -> Union[TransactionStatus, bson.ObjectId]:
    """Hace una transaccion entre usuarios

    Args:
        sender (EconomyUser): Usuario que envia la transaccion
        receptor (EconomyUser): Usuario que recive la transaccion
        quantity (float): Monto de la transaccion
        data_base_name (str): nombre de la base de datos de mongo
        type (TransactionType): Tipo de transaccion
        reason (str, optional): Razon de la transaccion. Defaults to ''.
        product (Product, optional): Producto si es compra por tienda. Defaults to None.
        admin (EconomyUser, optional): Administrador si es impresion o expropiacion. Defaults to None.

    Returns:
        Union[TransactionStatus, bson.ObjectId]: _description_
    """
    
    quantity = round(quantity, _global_settings.max_decimals)
    if quantity+((1/(10**(_global_settings.max_decimals+1)))*int(type == TransactionType.initial_coins)) <= 0.0:
        return TransactionStatus.negative_quantity, ''
            
    if type == TransactionType.initial_coins or type == TransactionType.forged:
        sender = EconomyUser(id_to_objectid(0))
    if type == TransactionType.shop_buy:
        reason = f"Compra de {product.title}"
    if type == TransactionType.admin_to_user:
        if sender is None:
            sender = EconomyUser(id_to_objectid(0))
            reason = "Impresion"
        if receptor is None:
            receptor = EconomyUser(id_to_objectid(0))
            reason = "Expropiacion"
            
    if sender._id == receptor._id:
        return TransactionStatus.sender_is_receptor, ''

    if receptor._id != id_to_objectid(0): #Not system
        receptor_exists = receptor.get_data_from_db()
        if not receptor_exists:
            return TransactionStatus.receptor_not_exists_not_exists, ''
    
        receptor.balance += quantity
        
    if sender._id != id_to_objectid(0): #Not system
        sender_exists = sender.get_data_from_db()
        if not sender_exists:
            return TransactionStatus.sender_not_exists, ''
        if sender.balance.value < quantity:
            return TransactionStatus.insufficient_coins, ''

        sender.balance -= quantity
    
    # Se hace el log de la transaccion
    transaction_log = TransactionLog(get_time(), type, sender, receptor, quantity, reason,
                                     product._id if product is not None else 0, admin._id if admin is not None else 0)
    transaccion_id = transaction_log.send_log_to_db(database_name).inserted_id

    return TransactionStatus.succesful, transaccion_id
