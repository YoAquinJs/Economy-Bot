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

    def __init__(self, user_id: int, user_name: str, final_balance: float, motive: str) -> None:
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
        sender (User): Usuario que envia la transaccion
        receiver (User): Usuario que recive la transaccion
        quantity (float): Monto de la transaccion
    """

    date: str = ''
    type: TransactionType = TransactionType.initial_coins
    sender: dict = {}
    receiver: dict = {}
    quantity: float = 0.0

    def __init__(self, date: str, type: TransactionType, sender: EconomyUser, receiver: EconomyUser, quantity: float):
        """Crea un TransactionLog

        Args:
            date (str): fecha de la transaccion
            type (str): tipo de transaccion
            sender (User): usuario que hace la transaccion
            receiver (User): usuario que recive la transaccion
            quantity (float): monto de la transaccion
            type (TransactionType): Tipo de transaccion
        """

        self.date = date
        self.type = type
        self.sender_id = sender._id
        self.receiver_id = receiver._id
        self.quantity = quantity

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
    
    user_id (int): Id del usuario que envia el bug
    user_name (str): Nombre del usuario envia el
    final_balance (float): Balance del usuario que se desregistra
    motive (str): Motivo del usuario que se desregistra
    """

    title: str = ''
    description: str = ''
    command: str = ''
    
    def __init__(self, title: str, description: str, command: str):
        """Crea un BugLog

        Args:
            title (str): titulo del reporte
            description (str): descripcion del bug
            command (str): comando que provoca el bug
        """
        
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
