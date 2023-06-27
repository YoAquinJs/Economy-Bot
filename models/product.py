"""Este modulo contiene el objeto modelo Producto para su uso en otros modulos"""

from typing import Union
from models.enums import CollectionNames, ProductStatus
from database import db_utils
from utils.utils import get_global_settings

global_settings = get_global_settings()


class Product:
    """Modelo de un Producto
    
    Attributes:
        _id (int): Id del producto
        user_id (int): Id del usuario propietario del producto
        title (str): Titulo del producto
        description (str): Titulo del producto
        price (float): Costo del producto
        database_name (str): Nombre de la base de datos del servidor
    """
    
    _id: int = 0
    user_id: int = 0
    title: str = ''
    description: str = ''
    price: float = 0.0
    database_name: str = ''
     
    def __init__(self, user_id: int, title: str, description: str, price: float, database_name: str):
        """Product init

        Args:
            user_id (int): id del que vemde el producto
            title (str): Titulo del que vemde el producto
            description (str): descripcion del que vemde el producto
            price (float): precio del que vemde el producto
            database_name (str): nombre de la base de datos de mongo
        """
        
        self.user_id = user_id
        self.title = title
        self.description = description
        self.price = round(price, global_settings.max_decimals)
        self.database_name = database_name

    @classmethod
    def from_database(cls, product_id: int, database_name: str) -> Union[object, bool]:
        """Genera un Product con informacion traida desde la base de datos

        Args:
            product_id (int): id del producto en la base de datos
            database_name (str): nombre de la base de datos de mongo

        Returns:
            Union[object, bool]: Producto, si existe el procto en la base de datos
        """
        
        product_id = int(product_id)
        data = db_utils.query('_id', product_id, database_name,  CollectionNames.shop.value)

        if data == None:
            return None, False

        return cls(
            data['user_id'],
            data['title'],
            data['description'],
            data['price'],
            database_name,
            data['_id']
        ), True

    @classmethod
    def from_dict(cls, dict):
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
        
        data = {
            '_id': self._id,
            'user_id': self.user_id,
            'price': self.price,
            'title': self.title,
            'description': self.description
        }
        
        db_utils.insert(data, self.database_name, CollectionNames.shop.value)

    def check_info(self) -> ProductStatus:
        """Verifica los datos del producto

        Returns:
            ProductStatus: Status de validacion de datos
        """
        
        if self.price <= 0.0:
            return ProductStatus.negative_quantity

        if self.title == '' or None:
            return ProductStatus.not_name

        user_exists = db_utils.exists(
            '_id', self.user_id, self.database_name, CollectionNames.users.value)
        if not user_exists:
            return ProductStatus.seller_does_not_exist

        return ProductStatus.succesful

    def modify_on_db(self, new_price=0.0, new_title='\0', new_description='\0'):
        """Realiza las modificacines pendientes en la base de datos

        Args:
            new_price (float, optional): Nuevo precio a modificar. Defaults to 0.0.
            new_title (str, optional): Nuevo titulo a modificar. Defaults to '\0'.
            new_description (str, optional): Nueva descripcion a modificar. Defaults to '\0'.
        """
        
        if new_price != 0.0:
            self.price = new_price
        if new_title != '\0':
            self.title = new_title
        if new_description != '\0':
            self.description = new_description

        data = {
            '_id': self._id,
            'user_id': self.user_id,
            'price': self.price,
            'title': self.title,
            'description': self.description
        }

        db_utils.replace('_id', self._id, data, self.database_name, CollectionNames.shop.value)

    def delete_on_db(self):
        """Elimina el producto en la base de datos
        """
        
        db_utils.delete('_id', self._id, self.database_name, CollectionNames.shop.value)

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
