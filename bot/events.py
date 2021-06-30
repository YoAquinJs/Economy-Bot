"""Discord Events"""

import discord

from bot.bot_utils import *
from bot.discord_client.discord_client import get_client
from database.db_utils import insert, modify, exists, query, delete, Collection

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
    if isinstance(error, commands.CommandNotFoundError):
        return
    print(error)
    msg = "ha ocurrido un error"
    if isinstance(error, commands.MissingRequiredArgument):
        msg = f"{msg}, faltan argumentos"
    elif isinstance(error, commands.ArgumentParsingError):
        msg = f"{msg}, un argumento no es valido"
    else:
        msg = f"{msg}, ah sido reportado a los desarrolladores"


    await send_message(ctx, msg)


# TODO specifc db
@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Sirve para controlar el sistema de la tienda del bot a través de reacciones.

    Args:
        payload (discord.RawReactionActionEvent): Es el payload de la reacción
    """

    guild = client.get_guild(payload.guild_id)

    if payload.member.bot or \
       exists("msg_id", payload.message_id, guild, Collection.shop.value) is False:
        return

    channel = discord.utils.get(client.get_guild(payload.guild_id).channels, id=payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)

    product = query("msg_id", payload.message_id, guild, Collection.shop.value)

    await msg.remove_reaction(payload.emoji, payload.member)

    seller_user = await client.fetch_user(product["UserID"])

    if payload.member.permissions_in(channel).administrator is True and str(payload.emoji) == "❌":
        await msg.delete()
        delete("msg_id", payload.message_id, guild, Collection.shop.value)

        await payload.member.send(f"has eliminado el producto {product['Name']}, del usuario {seller_user.name}, id"
                                  f" {seller_user.id}")
        await seller_user.send(f"tu producto {product['Name']} ah sido eliminado por el administrator "
                               f"{payload.member.name}, id {payload.member.id}")
    elif payload.member.id != product["UserID"]:
        if str(payload.emoji) != "🪙":
            return
        else:
            quantity = product["Price"]
            buyer_balance = query("user_id", payload.member.id, guild, Collection.balances.value)
            seller_balance = query("user_id", seller_user.id, guild, Collection.balances.value)

            # Si el comprador esta registrado
            if buyer_balance is not None:
                # Si el comprador tiene suficientes monedas
                if buyer_balance['balance'] >= quantity:
                    # if economic_users[author_key]["coins"] >= quantity:

                    buyer_balance['balance'] -= quantity
                    modify("user_id", buyer_balance['user_id'], "balance", buyer_balance['balance'], guild,
                           Collection.balances.value)

                    seller_balance['balance'] += quantity
                    modify("user_id", seller_balance['user_id'], "balance", buyer_balance['balance'], guild,
                           Collection.balances.value)

                    sale = {
                        "date": get_time(),
                        "type": "compra en tienda",
                        "buyer": buyer_balance['user_id'],
                        "seller": seller_balance['user_id'],
                        "quantity": quantity,
                        "product": product["Name"]
                    }

                    transaction = insert(sale, guild, Collection.transactions.value)

                    await payload.member.send(f"has adquirido el producto:{product['Name']}, del usuario:"
                                              f"{seller_user.name}; id:{seller_user.id}\n"
                                              f"id transaccion: {transaction.inserted_id}")
                    await seller_user.send(f"el usuario:{payload.member.name}; id:{payload.member.id} ah adquirido tu "
                                           f"producto:{product['Name']}, debes cumplir con la entrega\n"
                                           f"id transaccion: {transaction.inserted_id}")
                else:
                    await payload.member.send("no tienes suficientes monedas")
            else:
                await payload.member.send(f"no estas registrado, registrate con {global_settings['prefix']}registro")
            pass
    else:
        if str(payload.emoji) == "❌":
            await msg.delete()
            delete("msg_id", payload.message_id, guild, Collection.shop.value)

            await seller_user.send(f"has eliminado tu producto {product['Name']}")
