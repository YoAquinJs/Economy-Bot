from typing import List

from database.mongo_client import get_mongo_client
from models.enums import CollectionNames
from utils.utils import get_global_settings


class EconomyUser():
    """Sirve para identificar a un usuario en la economia y llevar el registro de sus monedas

    id (str): id del usuario
    name (str): nombre del usuario
    balance (float): moendas del nuevo usuario registrado en la economia
    roles (List[str]): roles del usuario.
    """
    _id: int = 0
    name: str = ''
    balance = None

    def __init__(self, _id: int, database_name: str = 'test_database',
                 name: str = '', roles: List[str] = []) -> None:
        """Crea un EconomyUser

        Args:
            _id (int): id del usuario
            name (str): nombre del usuario. Defaults to ''
            roles (List[str], optional): roles del usuario. Defaults to [].
            database_name (str, optional): nombre de la base de datos de mongo. Defaults to 'e_database'.

        Raises:
            NotFoundEconomyUser: Cuando el usuario no fue encontrado en la base de datos
            RegisteredUser: Cuando es un nuevo usuario y se quiere registar pero ya esta registrado
            ValueError: Cuando un usuario se registra su nombre no puede estar vacio
        """
        self.name = name
        self._id = _id
        self.roles = roles
        self.dbcollection = get_mongo_client(
        )[database_name][CollectionNames.users.value]

    def register(self) -> bool:
        """Registra al usuario a la economias

        Raises:
            ValueError: Cuando un usuario se registra su nombre no puede estar vacio

        Returns:
            bool: Se registro, si es False es porque el usuario ya estaba registrado
        """
        # Checa si el usuario no esta registrado
        db_result = self.dbcollection.find_one(
            {'_id': self.id}, {'_id': True})
        if db_result != None:
            return False

        if self.name == '':
            raise ValueError('Nombre vacio')

        # Registra al usuario
        gl = get_global_settings()
        self.dbcollection.insert_one({
            '_id': self._id,
            'name': self.name,
            'balance': gl.initial_number_of_coins
        })
        self.balance = Balance(0.0, self)

        return True

    def unregister(self):
        """Elimina al usuario de la base de datos"""
        self.dbcollection.delete_one({'_id': self._id})

    def get_balance_from_db(self) -> dict:
        """Trae los datos del usuario de la base de datos

        Returns:
            dict: Retorna un diccionario con el balance del usuario en Mongo o None si no lo encuentra
        """
        # se pide el balance del usuario desde la base de datos
        try:
            db_result = self.dbcollection.find_one({'_id': self.id}, {'balance': 1, 'name': 1, '_id': False})
            self.balance = Balance(db_result['balance'], self)
            self.name = db_result['name']

            return db_result
        except:
            return None

    def user_exists(self) -> bool:
        """Trae los datos del usuario de la base de datos

        Returns:
            bool: Dice si el usuario existe
        """
        # se pide el balance del usuario desde la base de datos
        db_result = self.dbcollection.find_one(
            {'_id': self.id}, {'balance': 1, 'name': 1, '_id': False})
        # Si el usuario no existe
        if db_result == None:
            return False

        self.balance = Balance(db_result['balance'], self)
        self.name = db_result['name']

        return True

    def get_data_from_dict(self, data):
        self._id = data['_id']
        self.name = data['name']
        self.balance = Balance(data['balance'], self)

    @property
    def id(self) -> int:
        return self._id


class Balance:
    def __init__(self, balance: float, user: EconomyUser):
        self.balance = balance
        self.user = user

    def __iadd__(self, add):
        self.user.dbcollection.update_one({'_id': self.user._id, }, {
            '$inc': {'balance': add}
        })
        self.balance += add

    def __isub__(self, sub):
        if self.balance < sub:
            self.user.dbcollection.update_one({'_id': self.user._id, }, {
                '$set': {'balance': 0.0}
            })

        self.user.dbcollection.update_one({'_id': self.user._id, }, {
            '$inc': {'balance': -sub}
        })

        self.balance -= sub

    def __repr__(self):
        return str(self.balance)

    def __str__(self):
        return str(self.balance)

    @property
    def value(self) -> float:
        return self.balance
