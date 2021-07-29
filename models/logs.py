from models.economy_user import EconomyUser
from database import db_utils
from database.db_utils import CollectionNames


class UnregisterLog:
    """UnregisterLog"""
    user_id: int = 0
    user_name: str = ''
    final_balance: float = 0.0
    motive: str = ''

    def __init__(self, user_id: int, user_name: str, final_balance: float, motive: str) -> None:
        """DesregisterLog init

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
    """TransactionLog"""
    date: str = ''
    type: str = ''
    sender: dict = {}
    receiver: dict = {}
    quantity: float = 0.0
    channel_name: str = ''

    def __init__(self, date: str, type: str, sender: EconomyUser, receiver: EconomyUser, quantity: float, channel_name: str):
        """TransactionLog init

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
        self.sender = {
            '_id': sender._id,
            'roles': sender.roles
        }
        self.receiver = {
            '_id': receiver._id,
            'roles': receiver.roles
        }
        self.quantity = quantity
        self.channel_name = channel_name

    def send_log_to_db(self, database_name: str):
        db_utils.insert(self.__dict__, database_name, CollectionNames.transactions.value)


class BugLog:
    """BugLog"""
    title: str = ''
    description: str = ''
    command: str = ''

    def __init__(self, description: str, command: str):
        """BogLog __init__

        Args:
            title (str): titulo del reporte
            description (str): descripcion del bug
            command (str): comando que provoca el bug
        """
        
        self.description = description
        self.command = command

    def send_log_to_db(self, database_name: str):
        db_utils.insert(self.__dict__, database_name, CollectionNames.bugs.value)
