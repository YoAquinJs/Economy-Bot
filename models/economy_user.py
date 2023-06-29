"""Este modulo contiene los objetos modelo EconomyUser y Balance para su uso en otros modulos"""

import bson
from typing import Union

from database import db_utils
from utils.utils import get_global_settings, id_to_objectid
from models.enums import CollectionNames

_global_settings = get_global_settings()


class EconomyUser():
    """Modelo de usuario en la economia

    Attributes:
        _id (bson.ObjectId): id del usuario
        name (str): nombre del usuario
        balance (float): moendas del nuevo usuario registrado en la economia
        database_name (str): Nombre de la base de datos del servidor de discord
    """
    
    _id: bson.ObjectId = None
    name: str = ''
    balance = None
    database_name = ''
    
    def __init__(self, _id: bson.ObjectId, database_name: str = 'none', name: str = '') -> None:
        """Crea un EconomyUser

        Args:
            _id (bson.ObjectId): id del usuario
            database_name(str, optional): Nombre de la base de datos del servidor de discord. Defaults to 'none'
            name (str, optional): nombre del usuario. Defaults to ''

        Raises:
            NotFoundEconomyUser: Cuando el usuario no fue encontrado en la base de datos
            RegisteredUser: Cuando es un nuevo usuario y se quiere registar pero ya esta registrado
            ValueError: Cuando un usuario se registra su nombre no puede estar vacio
        """
        
        self._id = _id
        self.name = name
        self.database_name = database_name

    def register(self) -> Union[bool, float]:
        """Registra al usuario a la economia

        Raises:
            ValueError: Cuando un usuario se registra su nombre no puede estar vacio

        Returns:
            Union[bool, float]: [Falso si el usuario ya estaba registrado, de contrario verdadero, balance inicial del usuario]
        """

        if self.name == '':
            raise ValueError('Nombre vacio')

        if db_utils.query("_id", self._id, self.database_name, CollectionNames.users.value) != None:
            return False, 0

        de_register = db_utils.query("user_id", self._id, self.database_name, CollectionNames.deregisters.value)
        
        if de_register is not None:
            initial_balance = de_register["final_balance"]
            db_utils.delete("_id", de_register["_id"], self.database_name, CollectionNames.deregisters.value)
        else:
            initial_balance = _global_settings.initial_number_of_coins
            
        db_utils.insert({
            '_id': self._id,
            'name': self.name,
            'balance': 0
        }, self.database_name, CollectionNames.users.value)

        return True, initial_balance

    def unregister(self):
        """Elimina al usuario de la base de datos
        """
        
        db_utils.delete('_id', self._id, self.database_name, CollectionNames.users.value)

    def get_data_from_db(self) -> bool:
        """Trae los datos del usuario de la base de datos

        Returns:
            bool: Dice si el usuario existe
        """

        db_result = db_utils.query('_id', self._id, self.database_name, CollectionNames.users.value)

        if db_result == None:
            return False

        self.balance = Balance(db_result['balance'], self)
        self.name = db_result['name']

        return True

    def get_data_from_dict(self, data: dict):
        """Llena las propiedades del objeto a partir de un diccionario

        Args:
            data (dict): Diccionario con los datos del EconomyUser

        """

        self._id = data['_id']
        self.name = data['name']
        self.balance = Balance(data['balance'], self)

    @property
    def id(self) -> bson.ObjectId:
        return self._id
    

    @classmethod
    def get_system_user(cls) -> object:
        """Retorna el usuario del sistema

        Returns:
            EconomyUser: Usuario para operaciones del sistema
        """
        
        return cls(id_to_objectid(0))


class Balance:
    """Modelo de balance de usuario

    Attributes:
        balance (float): Cantidad de monedas del usuario
        user (EconomyUser): Usuario que contiene el balance
    """

    balance = 0
    user = None
    
    def __init__(self, balance: float, user: EconomyUser):
        """Crea un Balance

        Args:
            balance (float): Cantidad de monedas del usuario
            user (EconomyUser): Usuario que contiene el 
        """

        self.balance = balance
        self.user = user


    def __iadd__(self, add):
        self.balance += add
        db_utils.modify("_id", self.user._id, "balance", self.balance, self.user.database_name, CollectionNames.users.value)
        return self

    def __isub__(self, sub):
        self.balance -= sub
        db_utils.modify("_id", self.user._id, "balance", self.balance, self.user.database_name, CollectionNames.users.value)
        return self


    def __repr__(self):
        return str(self.balance)

    def __str__(self):
        return str(self.balance)

    @property
    def value(self) -> float:
        return self.balance
