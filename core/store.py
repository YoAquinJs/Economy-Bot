from database.mongo_client import get_mongo_client
from typing import List
from utils.utils import get_global_settings
from database import db_utils
from models.product import Product
from models.enums import CollectionNames, ProductStatus

global_settings = get_global_settings()


def edit_product(product_id: int, user_id: int, database_name: str, new_price, new_title, new_description) -> ProductStatus:
    """Edita un producto, si son valores por default ese campo no se edita

    Args:
        product_id (int): id del producto
        user_id (int): id del usuario
        database_name (str): Nombre de la base de datos de mongo
        new_price (float, optional): nuevo precio. Defaults to 0.0.
        new_title (str, optional): nuevo titulo. Defaults to '0'.
        new_description (str, optional): nueva description. Defaults to '0'.

    Returns:
        ProductStatus: status de la modificacion
    """
    user_exists = db_utils.exists(
        '_id', user_id, database_name, CollectionNames.users.value)
    if not user_exists:
        return ProductStatus.seller_does_not_exist

    product, product_exists = Product.from_database(product_id, database_name)
    if not product_exists:
        return ProductStatus.no_exists_in_db

    if product.user_id != user_id:
        return ProductStatus.user_is_not_seller_of_product

    if new_price < 0.0:
        return ProductStatus.negative_quantity

    product.modify_on_db(new_price, new_title, new_description)
    return ProductStatus.succesful


def get_user_products(user_id: int, database_name: str) -> List[Product]:
    """Regresa un arreglo con los productos de un usuario de

    Args:
        user_id (id): id del usuario
        database_name (str): Nombre de la base de datos de mongo

    Returns:
        List[Product]: Productos del usuario
    """
    products = []
    mclient = get_mongo_client()
    products_query = mclient[database_name][CollectionNames.shop.value].find({
        'user_id': user_id
    })

    for p in products_query:
        p['database_name'] = database_name
        product = Product.from_dict(p)
        
        products.append(product)

    return products
