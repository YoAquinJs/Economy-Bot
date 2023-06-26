"""Este modulo contiene los objetos de los logs de la aplicacion"""

from models.economy_user import EconomyUser
from database import db_utils
from models.enums import CollectionNames


class UnregisterLog:
    """Modelo de un log de desregistro
    
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

    def send_log_to_db(self, database_name: str) -> str:
        """Manda un log a la base de datos de mongo

        Args:
            database_name ([type]): [description]

        Returns:
            str: id de la transacción
        """
        
        i = db_utils.insert(self.__dict__, database_name, CollectionNames.deregisters.value)
        return str(i.inserted_id)


class TransactionLog:
    """Modelo de un log de una transaccion
    
    date (str): Id del usuario que se desregistra
    type (int): Nombre del usuario que se desregistra
    sender (dict): Balance del usuario que se desregistra
    receiver (dict): Motivo del usuario que se desregistra
    quantity (float): Motivo del usuario que se desregistra
    channel_name (str): Canal en le cual se realizo la transaccion
    """

    date: str = ''
    type: str = ''
    sender: dict = {}
    receiver: dict = {}
    quantity: float = 0.0
    channel_name: str = ''

    def __init__(self, date: str, type: str, sender: EconomyUser, receiver: EconomyUser, quantity: float, channel_name: str):
        """Crea un TransactionLog

        Args:
            date (str): fecha de la transaccion
            type (str): tipo de transaccion
            sender (User): usuario que hace la transaccion
            receiver (User): usuario que recive la transaccion
            quantity (float): monto de la transaccion
            channel_name (str): canal donde se hizo la transaccion
        """

        self.date = date
        self.type = type
        self.sender_id = sender._id
        self.receiver_id = receiver._id
        self.quantity = quantity
        self.channel_name = channel_name

    def send_log_to_db(self, database_name: str) -> int:
        """Manda el log de la transaccion a la base de datos

        Args:
            database_name (str): Nombre de la base de datos del servidor de discord

        Returns:
            int: Id del registro del log de la transaccion
        """
        
        return db_utils.insert(self.__dict__, database_name, CollectionNames.transactions.value)


class BugLog:
    """Modelo de un log de un bug
    
    user_id (int): Id del usuario que se desregistra
    user_name (str): Nombre del usuario que se desregistra
    final_balance (float): Balance del usuario que se desregistra
    motive (str): Motivo del usuario que se desregistra
    """

    title: str = ''
    description: str = ''
    command: str = ''

    def __init__(self, title: str, description: str, command: str):
        """crea un BugLog

        Args:
            title (str): titulo del reporte
            description (str): descripcion del bug
            command (str): comando que provoca el bug
        """
        
        self.title = title
        self.description = description
        self.command = command

    def send_log_to_db(self, database_name: str):
        db_utils.insert(self.__dict__, database_name, CollectionNames.bugs.value)
