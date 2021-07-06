"""Discord Events"""

from core.transactions import new_transaction
from models.economy_user import EconomyUser
import discord
from discord.ext import commands

from bot.bot_utils import *
from utils.utils import get_global_settings
from bot.discord_client import get_client
from database.db_utils import exists, query, delete, CollectionNames

client = get_client()
global_settings = get_global_settings()


# region Events
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
        for dev_id in global_settings.dev_ids:
            dev = await client.fetch_user(dev_id)
            await dev.send(f"BUG REPORT: {error}")
        msg = f"{msg}, ah sido reportado a los desarrolladores"

    await send_message(ctx, msg)


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Sirve para controlar el sistema de la tienda del bot a través de reacciones.

    Args:
        payload (discord.RawReactionActionEvent): Es el payload de la reacción
    """

    guild = client.get_guild(payload.guild_id)
    database_name = get_database_name(guild)

    if payload.member.bot or \
       exists("_id", payload.message_id, database_name, CollectionNames.shop.value) is False:
        return

    channel = discord.utils.get(client.get_guild(
        payload.guild_id).channels, id=payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)

    product = query("_id", payload.message_id, database_name,
                    CollectionNames.shop.value)

    await msg.remove_reaction(payload.emoji, payload.member)

    seller_user = await client.fetch_user(product["user_id"])

    if payload.member.permissions_in(channel).administrator is True and str(payload.emoji) == "❌" and \
            payload.member.id != product["user_id"]:
        await msg.delete()
        delete("_id", payload.message_id, database_name,
               CollectionNames.shop.value)

        await payload.member.send(f"has eliminado el producto {product['title']}, del usuario {seller_user.name}, id"
                                  f" {seller_user.id}")
        await seller_user.send(f"tu producto {product['title']} ha sido eliminado por el administrator "
                               f"{payload.member.name}, id {payload.member.id}")
    elif payload.member.id != product["user_id"]:
        if str(payload.emoji) != "🪙":
            return
        else:
            quantity = product["price"]

            buyer_euser = EconomyUser(payload.member.id, database_name)
            seller_euser = EconomyUser(seller_user.id, database_name)

            # Si el comprador esta registrado
            if buyer_euser.get_data_from_db():
                # Si el comprador tiene suficientes monedas
                if buyer_euser.balance.value >= quantity:
                    # if economic_users[author_key]["coins"] >= quantity:
                    _, transaction = new_transaction(
                        buyer_euser, seller_euser, quantity, database_name, channel.name, 'compra en tienda')
                    
                    
                    await payload.member.send(f"has adquirido el producto: {product['title']}, del usuario: "
                                              f"{seller_user.name}; id: {seller_user.id}\n"
                                              f"id transaccion: {transaction}")
                    await seller_user.send(f"el usuario: {payload.member.name}; id: {payload.member.id} ha adquirido tu "
                                           f"producto: {product['title']}, debes cumplir con la entrega\n"
                                           f"id transaccion: {transaction}")
                else:
                    await payload.member.send("no tienes suficientes monedas")
            else:
                await payload.member.send(f"no estas registrado, registrate con {global_settings.prefix}registro")
            pass
    else:
        if str(payload.emoji) == "❌":
            await msg.delete()
            delete("_id", payload.message_id, database_name,
                   CollectionNames.shop.value)

            await seller_user.send(f"has eliminado tu producto {product['title']}")
