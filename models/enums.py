"""El modulo enums contiene clases Enum usadas en otros modulos que representan valores constantes"""

from enum import Enum


class CollectionNames(Enum):
    """Enum de las colecciones por servidor de discord en la base de datos"""

    bugs = "bugs"
    shop = "shop"
    forge = "forge"
    deregisters = "deregisters"
    users = "users"
    transactions = "transactions"


class TransactionStatus(Enum):
    """Enum del estado de la transaccion despues de procesarse"""

    negative_quantity = 'negative_quantity'
    sender_not_exists = 'sender_not_exists'
    receptor_not_exists = 'receptor_not_exists'
    sender_is_receptor = 'sender_is_receptor'
    insufficient_coins = 'insufficient_coins'
    succesful = 'succesful'


class ProductStatus(Enum):
    """Enum de los estados de un producto"""

    negative_quantity = 'negative_quantity'
    not_name = 'not_name'
    seller_does_not_exist = 'seller_does_not_exist'
    no_id = 'no_id'
    user_is_not_seller_of_product = 'user_is_not_seller_of_product'
    no_exists_in_db = 'no_exists_in_db'
    succesful = 'succesful'
