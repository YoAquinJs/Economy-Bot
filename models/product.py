from database.mongo_client import get_mongo_client
from typing import Union
from models.enums import CollectionNames, ProductStatus
from database import db_utils
from utils.utils import get_global_settings

global_settings = get_global_settings()


class Product:
    def __init__(self, user_id: int, title: str, description: str, price: float, database_name, _id: int = -1):
        """Product init

        Args:
            user_id (int): id del que vemde el producto
            title (str): Titulo del que vemde el producto
            description (str): descripcion del que vemde el producto
            price (float): precio del que vemde el producto
            database_name (str): nombre de la base de datos de mongo
            _id (int, optional): id del producto. Defaults to -1.
        """
        self._id = int(_id)
        self.user_id = user_id
        self.title = title
        self.description = description
        self.price = round(float(price), int(global_settings.max_decimals))
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
        data = db_utils.query('_id', product_id, database_name,
                              CollectionNames.shop.value)
        if data is None:
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
        data = {
            '_id': self._id,
            'user_id': self.user_id,
            'price': self.price,
            'title': self.title,
            'description': self.description
        }
        db_utils.insert(data, self.database_name, CollectionNames.shop.value)

    def check_info(self) -> ProductStatus:
        """Regresa None si no hay ningin error con los datos

        Returns:
            ProductStatus: status
        """
        if self.price <= 0.0:
            return ProductStatus.negative_quantity

        if self.title == '' or None:
            return ProductStatus.not_name

        user_exists = db_utils.exists(
            '_id', self.user_id, self.database_name, CollectionNames.users.value)
        if not user_exists:
            return ProductStatus.seller_does_not_exist

        return None

    def modify_on_db(self, new_price, new_title, new_description):
        if float(new_price) != 0:
            self.price = new_price
        if new_title != '0':
            self.title = new_title
        if new_description != '0':
            self.description = new_description

        data = {
            '_id': self._id,
            'user_id': self.user_id,
            'price': self.price,
            'title': self.title,
            'description': self.description
        }

        m_client = get_mongo_client()
        m_client[self.database_name][CollectionNames.shop.value].replace_one({
            '_id': self._id
        }, data)

    def delete_on_db(self):
        m_client = get_mongo_client()
        m_client[self.database_name][CollectionNames.shop.value].delete_one({
            '_id': self._id
        })

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
