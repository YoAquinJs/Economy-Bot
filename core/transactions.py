"""Este modulo se encarga de gestionar la creacion de un nuevo log de transaccion"""

import bson
from typing import Union

from utils.utils import get_time
from models.guild_settings import GuildSettings
from models.economy_user import EconomyUser
from models.product import Product
from models.logs import *
from models.enums import TransactionStatus, TransactionType


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
    
    system_user = EconomyUser.get_system_user()
    guild_settings = GuildSettings.from_database(database_name)

    quantity = round(quantity, guild_settings.max_decimals)
    if quantity+((1/(10**(guild_settings.max_decimals+1)))*int(type == TransactionType.initial_coins)) <= 0.0:
        return TransactionStatus.negative_quantity, ''
            
    if type == TransactionType.initial_coins or type == TransactionType.forged:
        sender = system_user
    if type == TransactionType.shop_buy:
        reason = f"Compra de {product.title}"
    if type == TransactionType.admin_to_user:
        admin_exists = admin.get_data_from_db()
        if admin_exists is False:
            return TransactionStatus.sender_not_exists
        
        if sender is None:
            sender = system_user
            reason = "Impresion"
        if receptor is None:
            receptor = system_user
            reason = "Expropiacion"
            
    if sender._id == receptor._id:
        return TransactionStatus.sender_is_receptor, ''

    if receptor._id != system_user._id: #Not system
        receptor_exists = receptor.get_data_from_db()
        if not receptor_exists:
            return TransactionStatus.receptor_not_exists, ''
    
        receptor.balance += quantity
        
    if sender._id != system_user._id: #Not system
        sender_exists = sender.get_data_from_db()
        if not sender_exists:
            return TransactionStatus.sender_not_exists, ''
        if sender.balance.value < quantity:
            return TransactionStatus.insufficient_coins, ''

        sender.balance -= quantity
    
    # Se hace el log de la transaccion
    transaction_log = TransactionLog(get_time(), type, sender._id, receptor._id, quantity, reason, 
                                     product._id if product is not None else None, admin._id if admin is not None else None)
    transaccion_id = transaction_log.send_log_to_db(database_name).inserted_id

    return TransactionStatus.succesful, transaccion_id
