import os
import json
import shutil
import discord
import datetime
import pytz

from client.client import client
from utils.utils import settings, server, get_global_settings
from db import bonobo_database

# region Events
@client.event
async def on_guild_join(guild):
    print(f"added {guild.name}, id: {guild.id}")
    new_settings = {
            "EconomicUsers": {},
            "Shop": {},
        }
    os.mkdir(f"local_settings/server_guild_{guild.id}")
    os.mkdir(f"local_settings/server_guild_{guild.id}/EconomyLogs")
    with open(f"local_settings/server_guild_{guild.id}/settings.json", "w") as guild_settings:
        json.dump(new_settings, guild_settings)


@client.event
async def on_ready():
    print("logged as")
    print(client.user.name)
    print(client.user.id)
    print('-----------')


@client.event
async def on_guild_remove(guild):
    print(f"removed {guild.name}, id: {guild.id}")
    shutil.rmtree(f"local_settings/server_guild_{guild.id}")


@client.event
async def on_raw_reaction_add(payload):
    guild = client.get_guild(payload.guild_id)
    local_settings = settings(guild)
    shop = local_settings["Shop"]
    channel = discord.utils.get(client.get_guild(payload.guild_id).channels, id=payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)

    if not(str(payload.message_id) in shop.keys()) or payload.member.bot:
        if not payload.member.bot and str(payload.message_id) in list(shop.keys()):
            await msg.remove_reaction(payload.emoji, payload.member)
        return

    await msg.remove_reaction(payload.emoji, payload.member)

    product = shop[str(payload.message_id)]
    seller_user = await client.fetch_user(product["UserID"])

    if payload.member.id != product["UserID"]:
        print(product["UserID"])
        print(payload.member.id)
        if str(payload.emoji) != "🪙":
            return
        else:
            quantity = product["Price"]
            economic_users = local_settings["EconomicUsers"]
            receptor_key = f"{seller_user.name}_{seller_user.id}"
            author_key = f"{payload.member.name}_{payload.member.id}"

            if author_key in economic_users.keys():
                if economic_users[author_key]["coins"] >= quantity:
                    economic_users[author_key]["coins"] -= quantity
                    economic_users[receptor_key]["coins"] += quantity

                    tran_bson = {
                        "date": str(datetime.datetime.now(pytz.utc)),
                        "type": "compra en tienda",
                        "sender": author_key,
                        "receptor": receptor_key,
                        "quantity": quantity,
                        "product": product["Name"]
                    }

                    bonobo_database.send_transaction(tran_bson)

                    local_settings["EconomicUsers"] = economic_users
                    json.dump(local_settings, open(f"{server(guild)}/settings.json", "w"))
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
            del shop[str(payload.message_id)]
            local_settings["Shop"] = shop
            json.dump(local_settings, open(f"{server(guild)}/settings.json", "w"))
            await seller_user.send(f"tu producto {product['Name']} ah sido eliminado")
