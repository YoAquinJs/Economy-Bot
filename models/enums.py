from enum import Enum


class CollectionNames(Enum):
    bugs = "bugs"
    shop = "shop"
    forge = "forge"
    deregisters = "deregisters"
    users = "users"
    transactions = "transactions"


class TransactionStatus(Enum):
    negative_quantity = 'negative_quantity'
    sender_not_exists = 'sender_not_exists'
    receptor_not_exists = 'receptor_not_exists'
    sender_is_receptor = 'sender_is_receptor'
    insufficient_coins = 'insufficient_coins'
    succesful = 'succesful'
