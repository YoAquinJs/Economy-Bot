"""Este modulo contiene los objetos de los logs de la aplicacion"""

import pymongo

from models.economy_user import EconomyUser
from database import db_utils
from models.enums import CollectionNames, TransactionType


class UnregisterLog:
    """Modelo de un log de desregistro
    
    Attributes:
        user_id (int): Id del usuario que se desregistra
        user_name (str): Nombre del usuario que se desregistra
        final_balance (float): Balance del usuario que se desregistra
        motive (str): Motivo del usuario que se desregistra
    """
    
    user_id: int = 0
    user_name: str = ''
    final_balance: float = 0.0
    motive: str = ''

    def __init__(self, user_id: int, user_name: str, final_balance: float, motive: str):
        """Crea un UnregisterLog

        Args:
            user_id (int): User de un usuario de discord
            user_name (str): Nombre del usuario de discord
            final_balance (float): Total de monedas
            motive (str): motivo
        """
        
        self.user_id = user_id
        self.user_name = user_name
        self.final_balance = final_balance
        self.motive = motive

    def send_log_to_db(self, database_name: str):
        """Manda un log a la base de datos de mongo

        Args:
            database_name (str): Nombre de la base de datos del servidor de discord
        """
        
        db_utils.insert(self.__dict__, database_name, CollectionNames.deregisters.value)


class TransactionLog:
    """Modelo de un log de una transaccion
    
    Attributes:
        date (str): Id del usuario que se desregistra
        type (TransactionType): Tipo de transaccion
        sender_id (int): Usuario que envia la transaccion
        receiver_id (int): Usuario que recive la transaccion
        quantity (float): Monto de la transaccion
        reason (str): Razon de la transaccion
        product_id (int): Id del producto en caso de ser compra por tienda
        admin_id (int): Id del administrador de caso de ser impresion/expropiacion
    """

    date: str = ''
    type: TransactionType = TransactionType.initial_coins
    sender_id: int = 0
    receiver_id: int = 0
    quantity: float = 0.0
    reason: str = '' 
    product_id: int = 0
    admin_id: int = 0

    def __init__(self, date: str, type: TransactionType, sender: EconomyUser, receiver: EconomyUser, quantity: float, reason: str = '', product_id: int = 0, admin_id: int = 0):
        """Crea un TransactionLog

        Args:
            date (str): Fecha de la transaccion
            type (str): Tipo de transaccion
            sender (EconomyUser): Usuario que hace la transaccion
            receiver (EconomyUser): Usuario que recive la transaccion
            quantity (float): Monto de la transaccion
            type (TransactionType): Tipo de transaccion
            reason (str, optional): Razon de la transaccion. Defaults to ''.
            product_id (int, optional): Id del producto en caso de ser compra por tienda. Defaults to 0.
            admin_id (int, optional): Id del administrador de caso de ser impresion/expropiacion. Defaults to 0.
        """

        self.date = date
        self.type = type
        self.sender_id = sender._id
        self.receiver_id = receiver._id
        self.quantity = quantity
        self.reason = reason
        self.product_id = product_id
        self.admin_id = admin_id

    def send_log_to_db(self, database_name: str) -> pymongo.results.InsertOneResult:
        """Manda el log de la transaccion a la base de datos

        Args:
            database_name (str): Nombre de la base de datos del servidor de discord

        Returns:
            pymongo.results.InsertOneResult: Contiene la información de la inserción en MongoDB
        """
        
        return db_utils.insert({**self.__dict__, "type": self.type.value}, database_name, CollectionNames.transactions.value)


class BugLog:
    """Modelo de un log de un bug
    
    Attributes:
        user_id (int): Id del usuario que envia el bug
        title (str): Titulo del bug
        description (str): Descripcion del bug
        command (str): Nombre del comando en donde surgio el bug
    """

    user_id: int = 0
    title: str = ''
    description: str = ''
    command: str = ''
    
    def __init__(self, user_id: int, title: str, description: str, command: str):
        """Crea un BugLog

        Args:
            user_id (int): Id del usuario que envia el bug
            title (str): titulo del reporte
            description (str): descripcion del bug
            command (str): comando que provoca el bug
        """
        
        self.user_id = user_id
        self.title = title
        self.description = description
        self.command = command

    def send_log_to_db(self, database_name: str) -> pymongo.results.InsertOneResult:
        """Manda el log del bug a la base de datos

        Args:
            database_name (str): Nombre de la base de datos del servidor de discord
            
        Returns:
            pymongo.results.InsertOneResult: Contiene la información de la inserción en MongoDB
        """

        return db_utils.insert(self.__dict__, database_name, CollectionNames.bugs.value)
