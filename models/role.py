from typing import Union

from database import db_utils
from database.mongo_client import get_mongo_client
import utils.utils
from utils.utils import get_global_settings
from models.enums import CollectionNames, ProductStatus

global_settings = get_global_settings()


class Role:
    def __init__(self, user_id: int, title: str, description: str, price: float, image: str, role: int,
                 max_sells: int, sells: int, edits: list, database_name, _id: int = -1):
        """Product init

        Args:
            user_id (int): id del que vende el rol
            title (str): Titulo del rol
            description (str): descripcion del rol
            price (float): precio del rol
            image (str): url de la imagen o 'none' si es nula
            role (discord.Role): rol a asginar en la venta
            max_sells (int): maximo numero de ventas
            edits (list): lista de ediciones del rol
            database_name (str): nombre de la base de datos de mongo
            _id (int, optional): id del rol. Defaults to -1.
        """
        self._id = int(_id)
        self.user_id = user_id
        self.title = title
        self.description = description
        self.price = price
        self.image = image
        self.role = role
        self.max_sells = max_sells
        self.sells = sells
        self.edits = edits
        self.database_name = database_name

    @classmethod
    def from_database(cls, role_id: int, database_name: str) -> Union[object, bool]:
        """Genera un Product con informacion traida desde la base de datos

        Args:
            role_id (int): id del rol en la base de datos
            database_name (str): nombre de la base de datos de mongo

        Returns:
            Union[object, bool]: Objeto Role, si existe el rol en la base de datos
        """

        role_id = int(role_id)
        data = db_utils.query('_id', role_id, database_name, CollectionNames.role_shop.value)

        if data is None:
            return None, False

        return cls(
            data["user_id"],
            data["title"],
            data["description"],
            data["price"],
            data["image"],
            data["role"],
            data["max_sells"],
            data["sells"],
            data["edits"],
            database_name,
            data["_id"]
        ), True

    @classmethod
    def from_dict(cls, dict):
        """Regresa un nuevo objeto con la informacion de in diccionario

        Args:
            dict (dict): diccionario con los atributos del rol

        Returns:
            Role: instancia de Role
        """
        return cls(**dict)

    def send_to_db(self):
        data = {
            '_id': self._id,
            'user_id': self.user_id,
            'price': self.price,
            'title': self.title,
            'description': self.description,
            'image': self.image,
            'role': self.role,
            'max_sells': self.max_sells,
            'sells': self.sells,
            'edits': self.edits
        }
        db_utils.insert(data, self.database_name, CollectionNames.role_shop.value)

    def check_info(self) -> ProductStatus:
        """Regresa None si no hay ningin error con los datos

        Returns:
            ProductStatus: status
        """
        if self.price <= 0.0:
            return ProductStatus.negative_quantity

        if self.title == '' or None:
            return ProductStatus.not_name

        if self.max_sells < 0:
            return ProductStatus.negative_max_sells

        user_exists = db_utils.exists(
            '_id', self.user_id, self.database_name, CollectionNames.users.value)
        if not user_exists:
            return ProductStatus.seller_does_not_exist

        return None

    def modify_on_db(self, new_price, new_title, new_description, new_image, new_role, sells):
        edit_log = f"{utils.utils.get_time()}: "
        if float(new_price) != 0:
            edit_log += f"{new_price}, "
            self.price = new_price
        if new_title != '0':
            edit_log += f"{new_title}, "
            self.title = new_title
        if new_description != '0':
            edit_log += f"{new_description}, "
            self.description = new_description
        if new_image != '0':
            edit_log += f"{new_image}, "
            self.image = new_image
        if new_role != '0':
            edit_log += f"{new_image}, "
            self.image = new_image

        self.edits.append(edit_log + f"Ventas: {sells}")

        data = {
            '_id': self._id,
            'user_id': self.user_id,
            'price': self.price,
            'title': self.title,
            'description': self.description,
            "image": self.image,
            "role": self.role,
            "max_sells": self.max_sells,
            'sells': self.sells,
            'edits': self.edits
        }

        m_client = get_mongo_client()
        m_client[self.database_name][CollectionNames.role_shop.value].replace_one({
            '_id': self._id
        }, data)

    def delete_on_db(self):
        m_client = get_mongo_client()
        m_client[self.database_name][CollectionNames.role_shop.value].delete_one({
            '_id': self._id
        })

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
