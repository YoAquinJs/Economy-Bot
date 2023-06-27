"""Este modulo contiene los callback de eventos de discord"""

import discord
from discord.ext import commands

from bot.bot_utils import *
from bot.discord_client import get_client

from core.logger import report_bug_log
from core.transactions import new_transaction
from utils.utils import get_global_settings
from models.economy_user import EconomyUser
from models.enums import TransactionStatus, TransactionType

from database.db_utils import exists, query, delete, CollectionNames

client = get_client()
global_settings = get_global_settings()


@client.event
async def on_ready():
    """Imprime información del cliente cuando el bot ya está en línea
    """
    
    print("logged as")
    print(client.user.name)
    print(client.user.id)
    print('-----------')


@client.event
async def on_command_error(ctx, error):
    """Gestiona los errores que surgen en el procesamiento de los comandos

    Args:
        ctx (discord.ext.commands.Context): Context de discord
        error (discord.ext.commands.CommandError): TError lanzado en el comando
    """
    
    if isinstance(error, commands.CommandNotFound):
        return

    msg = "ha ocurrido un error"
    if isinstance(error, commands.MissingRequiredArgument):
        msg = f"{msg}, faltan argumentos"
    elif isinstance(error, commands.BadArgument):
        msg = f"{msg}, un argumento no es valido"
    elif isinstance(error, commands.TooManyArguments):
        msg = f"{msg}, demasiados argumentos"
    elif isinstance(error, commands.MissingPermissions):
        msg = f"{msg}, no tienes permisos para realizar esta accion"
    elif isinstance(error, commands.BotMissingPermissions):
        msg = f"{msg}, de bot no tiene permisos para realizar esta accion"
    else:
        error = f"exception in {ctx.command.name}: {error}"
        print(error)
        report_bug_log(ctx.author.id, "Command Error", error, ctx.command.name, get_database_name(ctx.guild))
        msg = f"{msg}, ya ah sido reportado a los desarrolladores"

    await send_message(ctx, msg)


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Evento de reaccion a un mensaje del bot, utilizado para el sistema de tienda

    Args:
        payload (discord.RawReactionActionEvent): Es el payload de la reacción
    """

    guild = client.get_guild(payload.guild_id)
    database_name = get_database_name(guild)

    #Vericar que el usuario no sea un bot, y que el mensaje este registrado como producto
    if payload.member.bot or not exists("_id", payload.message_id, database_name, CollectionNames.shop.value):
        return

    channel = discord.utils.get(client.get_guild(payload.guild_id).channels, id=payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    await msg.remove_reaction(payload.emoji, payload.member)

    product = query("_id", payload.message_id, database_name, CollectionNames.shop.value)

    seller_user = await client.fetch_user(product["user_id"])

    if payload.member.id == product["user_id"]:
        if str(payload.emoji) == "❌":
            await msg.delete()
            delete("_id", payload.message_id, database_name, CollectionNames.shop.value)
            await seller_user.send(f"has eliminado tu producto {product['title']}")

    else:
        if str(payload.emoji) == "❌":
            if channel.permissions_for(payload.member).administrator: #Admin removal TODO to role checking
                await msg.delete()
                delete("_id", payload.message_id, database_name, CollectionNames.shop.value)

                await payload.member.send(f"Has eliminado el producto {product['title']}, del usuario {seller_user.name}, id"
                                          f" {seller_user.id}. Como administrador de {global_settings.economy_name}")
                await seller_user.send(f"Tu producto {product['title']} ha sido eliminado por el administrator "
                                       f"{payload.member.name}, id {payload.member.id}")
        elif str(payload.emoji) == "🪙": #Buyer
            quantity = product["price"]

            buyer_euser = EconomyUser(payload.member.id, database_name)
            seller_euser = EconomyUser(seller_user.id, database_name)

            status, transaction_id = new_transaction(buyer_euser, seller_euser, quantity, database_name, channel.name, TransactionType.shop_buy)
            
            if status == TransactionStatus.sender_not_exists:
                await payload.member.send(f"Para realizar la compra del producto, registrate con {global_settings.prefix}registro en algun canal del servidor.")
            elif status == TransactionStatus.insufficient_coins:
                await payload.member.send(f"No tienes suficientes {global_settings.coin_name} para realizar la compra del producto {product['title']}.")
            elif status == TransactionStatus.succesful:
                await payload.member.send(f"Has adquirido el producto: {product['title']}, del usuario: {seller_user.name}; Id: {seller_user.id}\n"
                                          f"Id transaccion: {transaction_id}. Tu saldo actual es de {buyer_euser.balance.value} {global_settings.coin_name}.")
                await seller_user.send(f"El usuario: {payload.member.name}; id: {payload.member.id} ha adquirido tu producto: {product['title']}, debes cumplir con la entrega\n"
                                       f"id transaccion: {transaction_id}. Tu saldo actual es de {seller_euser.balance.value} {global_settings.coin_name}.")
