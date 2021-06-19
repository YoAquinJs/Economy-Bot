import shutil
import discord

from utils.utils import *
from db import balances_db, shop_db
from client.client import get_client

client = get_client()


# region Events
@client.event
async def on_guild_join(guild: discord.Guild):
    init_server(guild)


@client.event
async def on_ready():
    print("logged as")
    print(client.user.name)
    print(client.user.id)
    print('-----------')


# @client.event
# async def on_command_error(ctx, error):
#     print(error)
#     msg = "ha ocurrido un error"
#     if isinstance(error, commands.MissingRequiredArgument):
#         msg = f"{msg}, faltan argumentos"
#         pass
#     elif isinstance(error, commands.ArgumentParsingError):
#         msg = f"{msg}, un argumento no es valido"
#         pass
#     elif isinstance(error, commands.MissingRequiredArgument):
#         msg = f"{msg}, faltan argumentos"
#         pass
#
#     await send_message(ctx, msg)


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.member.bot:
        return

    guild = client.get_guild(payload.guild_id)
    channel = discord.utils.get(client.get_guild(
        payload.guild_id).channels, id=payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)

    product = shop_db.find_product(payload.message_id, guild)

    await msg.remove_reaction(payload.emoji, payload.member)

    seller_user = await client.fetch_user(product["UserID"])

    if payload.member.permissions_in(channel).administrator is True and str(payload.emoji) == "❌":
        await msg.delete()

        shop_db.delete_product(payload.message_id, guild)

        await payload.member.send(f"has eliminado el producto {product['Name']}, del usuario {seller_user.name}, id"
                                  f" {seller_user.id}")
        await seller_user.send(f"tu producto {product['Name']} ah sido eliminado por el administrator "
                               f"{payload.member.name}, id {payload.member.id}")

    elif payload.member.id != product["UserID"]:
        if str(payload.emoji) != "🪙":
            return
        else:
            quantity = product["Price"]
            buyer_balance = balances_db.get_balance(payload.member.id, guild)
            seller_balance = balances_db.get_balance(seller_user.id, guild)

            # Si el comprador esta registrado
            if buyer_balance != None:
                # Si el comprador tiene suficientes monedas
                if buyer_balance['balance'] >= quantity:
                    # if economic_users[author_key]["coins"] >= quantity:

                    buyer_balance['balance'] -= quantity
                    balances_db.modify_balance(
                        buyer_balance['user_id'], buyer_balance['balance'], guild)

                    seller_balance['balance'] += quantity
                    balances_db.modify_balance(
                        seller_balance['user_id'], seller_balance['balance'], guild)

                    sale = {
                        "date": get_time(),
                        "type": "compra en tienda",
                        "buyer": buyer_balance['user_id'],
                        "seller": seller_balance['user_id'],
                        "quantity": quantity,
                        "product": product["Name"]
                    }

                    shop_db.new_sale(sale, guild)

                    await payload.member.send(f"has adquirido el producto:{product['Name']}, del usuario:"
                                              f"{seller_user.name}; id:{seller_user.id}")
                    await seller_user.send(f"el usuario:{payload.member.name}; id:{payload.member.id} ah adquirido tu "
                                           f"producto:{product['Name']}, debes cumplir con la entrega")
                else:
                    await payload.member.send("no tienes suficientes monedas")
            else:
                global_settings = get_global_settings()
                await payload.member.send(f"no estas registrado, registrate con {global_settings['prefix']}regis")
            pass
    else:
        if str(payload.emoji) == "❌":
            await msg.delete()

            shop_db.delete_product(payload.message_id, guild)

            await seller_user.send(f"has eliminado tu producto {product['Name']}")


@client.event
async def on_guild_remove(guild: discord.Guild):
    print(f"removed {guild.name}, id: {guild.id}")
    shutil.rmtree(f"local_settings/server_guild_{guild.id}")
