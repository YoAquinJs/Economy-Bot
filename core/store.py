"""Este modulo se encarga de funcionalidades relacionadas al manejo de productos de usuarios"""

import bson
import discord
from typing import List

from database import db_utils
from bot.discord_client import get_client
from utils.utils import get_global_settings, objectid_to_id, id_to_objectid

from models.economy_user import EconomyUser
from models.product import Product
from models.enums import CollectionNames, TransactionStatus, TransactionType
from core.transactions import new_transaction

global_settings = get_global_settings()
client = get_client()


async def reaction_to_product(product: Product, emoji: str, reactant: discord.Member, channel: discord.TextChannel, database_name: str) -> bool:
    """Logica de reaccion a un producto para compras o para eliminarlo

    Args:
        product (Product): Producto al que se reacciono
        emoji (str): Emoji de reaccion
        reactant (discord.Member): Usuario que reacciono al producto
        channel (discord.TextChannel): Canal de discord en el que se encuentra el usuario
        database_name (str): Nombre de la base de datos del servidor de discord
        
    Returns:
        bool: Si se elimina el mensaje del producto o no
    """
    
    seller_user = await client.fetch_user(objectid_to_id(product.user_id))
    
    if reactant.id == seller_user.id:
        if emoji == "❌": # Seller removal
            db_utils.delete("_id", product._id, database_name, CollectionNames.shop.value)
            await seller_user.send(f"has eliminado tu producto {product.title}")
            return True
    else:
        if emoji == "❌": #Admin removal
            if channel.permissions_for(reactant).administrator: #Admin removal TODO to role checking
                db_utils.delete("_id", product._id, database_name, CollectionNames.shop.value)

                await reactant.send(f"Has eliminado el producto {product.title}, del usuario {seller_user.name}, id"
                                          f" {seller_user.id}. Como administrador de {global_settings.economy_name}")
                await seller_user.send(f"Tu producto {product.title} ha sido eliminado por el administrator "
                                       f"{reactant.name}, id {reactant.id}")
                return True
        elif emoji == "🪙": #Buyer
            buyer_euser = EconomyUser(id_to_objectid(reactant.id), database_name)
            seller_euser = EconomyUser(id_to_objectid(seller_user.id), database_name)

            status, transaction_id = new_transaction(buyer_euser, seller_euser, product.price, database_name, TransactionType.shop_buy, product=product)
            
            if status == TransactionStatus.sender_not_exists:
                await reactant.send(f"Para realizar la compra del producto, registrate con {global_settings.prefix}registro en algun canal del servidor.")
            elif status == TransactionStatus.insufficient_coins:
                await reactant.send(f"No tienes suficientes {global_settings.coin_name} para realizar la compra del producto {product.title}.")
            elif status == TransactionStatus.succesful:
                await reactant.send(f"Has adquirido el producto: {product.title}, del usuario: {seller_user.name}; ID: {seller_user.id}\n"
                                          f"Id transaccion: {transaction_id}. Tu saldo actual es de {buyer_euser.balance.value} {global_settings.coin_name}.")
                await seller_user.send(f"El usuario: {buyer_euser.name}; ID: {reactant.id} ha adquirido tu producto: {product.title}, debes cumplir con la entrega\n"
                                       f"ID transaccion: {transaction_id}. Tu saldo actual es de {seller_euser.balance.value} {global_settings.coin_name}.")
                
        return False



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
