from enum import Enum


class CollectionNames(Enum):
    bugs = "bugs"
    shop = "shop"
    role_shop = "role_shop"
    forge = "forge"
    deregisters = "deregisters"
    users = "users"
    transactions = "transactions"
    bugs_bl = "bugs_bl"
    shop_bl = "shop_bl"
    register_bl = "register_bl"
    transactions_bl = "transactions_bl"


class TransactionStatus(Enum):
    negative_quantity = 'negative_quantity'
    sender_not_exists = 'sender_not_exists'
    receptor_not_exists = 'receptor_not_exists'
    sender_is_receptor = 'sender_is_receptor'
    insufficient_coins = 'insufficient_coins'
    succesful = 'succesful'


class ProductStatus(Enum):
    sold_out = 'sold_out'
    negative_quantity = 'negative_quantity'
    negative_max_sells = 'negative_max_sells'
    not_name = 'not_name'
    seller_does_not_exist = 'seller_does_not_exist'
    no_id = 'no_id'
    user_is_not_seller_of_product = 'user_is_not_seller_of_product'
    no_exists_in_db = 'no_exists_in_db'
    succesful = 'succesful'


class BlackLists(Enum):
    register = "r"
    bug_report = "b"
    shop = "s"
    transactions = "t"

