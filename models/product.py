"""Este modulo contiene el objeto modelo Producto para su uso en otros modulos"""

import bson
from typing import Union

from database import db_utils
from models.enums import CollectionNames, ProductStatus
from models.guild_settings import GuildSettings


class Product:
    """Modelo de un Producto
    
    Attributes:
        _id (bson.ObjectId): Id del producto
        user_id (bson.ObjectId): Id del usuario propietario del producto
        channel_id (bson.ObjectId): Id del canal donde se encuentra el producto
        title (str): Titulo del producto
        description (str): Titulo del producto
        price (float): Costo del producto
        database_name (str): Nombre de la base de datos del servidor de discord
    """
    
    _id: bson.ObjectId = None
    user_id: bson.ObjectId = None
    channel_id: bson.ObjectId = None
    title: str = ''
    description: str = ''
    price: float = 0.0
    database_name: str = ''
     
    def __init__(self, user_id: bson.ObjectId, channel_id: bson.ObjectId, title: str, description: str, price: float, database_name: str, _id: bson.ObjectId = None):
        """Crea un producto

        Args:
            user_id (bson.ObjectId): Id del usuario que oferta el producto
            channel_id (bson.ObjectId): Id del canal donde se encuentra el producto
            title (str): Titulo del que vemde el producto
            description (str): Descripcion del que vemde el producto
            price (float): Precio del que vemde el producto
            database_name (str): Nombre de la base de datos del servidor de discord
        """
        
        self.user_id = user_id
        self.channel_id = channel_id
        self.title = title
        self.description = description
        self.price = round(price, GuildSettings.from_database(database_name).max_decimals)
        self.database_name = database_name
        self._id = _id

    @classmethod
    def from_database(cls, product_id: bson.ObjectId, database_name: str) -> Union[object, bool]:
        """Genera un Product con informacion traida desde la base de datos

        Args:
            product_id (bson.ObjectId): id del producto en la base de datos
            database_name (str): Nombre de la base de datos del servidor de discord

        Returns:
            Union[object, bool]: Producto, si existe el procto en la base de datos
        """
        
        data = db_utils.query('_id', product_id, database_name,  CollectionNames.shop.value)

        if data == None:
            return None, False

        return cls(
            data['user_id'],
            data['channel_id'],
            data['title'],
            data['description'],
            data['price'],
            database_name,
            data['_id']
        ), True

    @classmethod
    def from_dict(cls, dict: dict) -> object:
        """Regresa un nuevo objeto con la informacion de in diccionario

        Args:
            dict (dict): diccionario con los atributos del product

        Returns:
            Producto: instancia de Producto
        """
        
        return cls(**dict)

    def send_to_db(self):
        """Registra el producto en la base de datos
        """
        
        db_utils.insert( {key: value for key, value in self.__dict__.items() if key != "database_name"}, self.database_name, CollectionNames.shop.value)

    def check_info(self) -> ProductStatus:
        """Verifica los datos del producto

        Returns:
            ProductStatus: Status de validacion de datos
        """
        
        if self.price <= 0.0:
            return ProductStatus.negative_quantity

        if self.title == '' or None:
            return ProductStatus.not_name

        user_exists = db_utils.exists('_id', self.user_id, self.database_name, CollectionNames.users.value)

        if not user_exists:
            return ProductStatus.seller_does_not_exist

        return ProductStatus.succesful

    def delete_on_db(self):
        """Elimina el producto en la base de datos
        """
        
        db_utils.delete('_id', self._id, self.database_name, CollectionNames.shop.value)

    @property
    def id(self) -> bson.ObjectId:
        return self._id

    @id.setter
    def id(self, value: bson.ObjectId):
        self._id = value
