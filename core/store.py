"""Este modulo se encarga de funcionalidades relacionadas al manejo de productos de usuarios"""

import bson
from typing import List

from utils.utils import get_global_settings
from database import db_utils
from models.product import Product
from models.enums import CollectionNames, ProductStatus

global_settings = get_global_settings()


def get_user_products(user_id: bson.ObjectId, database_name: str) -> List[Product]:
    """Regresa un arreglo con los productos de un usuario de

    Args:
        user_id (bson.ObjectId): id del usuario
        database_name (str): Nombre de la base de datos del servidor de discord

    Returns:
        List[Product]: Productos del usuario
    """
    
    products = []
    products_query = db_utils.query('user_id', user_id, database_name, CollectionNames.shop.value, True)
    
    for p in products_query:
        p['database_name'] = database_name
        product = Product.from_dict(p)
        
        products.append(product)

    return products
