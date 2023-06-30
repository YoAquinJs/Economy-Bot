"""El modulo enums contiene clases Enum usadas en otros modulos que representan valores constantes"""

from enum import Enum


class CollectionNames(Enum):
    """Enum de las colecciones por servidor de discord en la base de datos"""

    bugs = "bugs"
    shop = "shop"
    users = "users"
    deregisters = "deregisters"
    transactions = "transactions"
    settings = "settings"
    
class TransactionStatus(Enum):
    """Enum del estado de la transaccion despues de procesarse"""

    succesful = 'succesful'
    negative_quantity = 'negative_quantity'
    sender_not_exists = 'sender_not_exists'
    sender_is_receptor = 'sender_is_receptor'
    insufficient_coins = 'insufficient_coins'
    receptor_not_exists = 'receptor_not_exists'

class TransactionType(Enum):
    """Enum del tipo de transaccion"""

    forged = 'forged' #From system
    shop_buy = 'shop_buy'
    user_to_user = 'user_to_user'
    initial_coins = 'initial_coins' #From system
    admin_to_user = 'admin_to_user' #From system

class ProductStatus(Enum):
    """Enum de los estados de un producto"""

    no_id = 'no_id'
    not_name = 'not_name'
    succesful = 'succesful'
    no_exists_in_db = 'no_exists_in_db'
    negative_quantity = 'negative_quantity'
    seller_does_not_exist = 'seller_does_not_exist'
    user_is_not_seller_of_product = 'user_is_not_seller_of_product'

class CommandNames(Enum):
    """Enum de los nombres de los comandos"""

    ping = 'ping'
    ayuda = 'ayuda'
    bug = 'bug'
    registro = 'registro'
    desregistro = 'desregistro'
    balance = 'balance'
    usuario = 'usuario'
    transferir = 'transferir'
    validar = 'validar'
    producto = 'producto'
    productos = 'productos'
    delproducto = 'delproducto'
    adminayuda = 'adminayuda'
    imprimir = 'imprimir'
    expropiar = 'expropiar'
    initforge = 'initforge'
    stopforge = 'stopforge'
    reset = 'reset'
    serverconfig = 'serverconfig'
    