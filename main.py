import os
import json
import pytz
import shutil
import asyncio
import discord
import datetime
from random import randint
from discord.ext import commands

from db import bonobo_database

# region Settings
# los settings globales aplican a todos los servidores en que se encuentre el bot (prefix, token, )
with open("settings.json", "r") as tmp:
    global_settings = json.load(tmp)

intents = discord.Intents.default()
intents.members = True


client = commands.Bot(command_prefix=global_settings["prefix"], help_command=None,
                      activity=discord.Game(f"Migala Bot | {global_settings['prefix']}help"),
                      status=discord.Status.online, intents=intents)

intents = discord.Intents(members=True)
welcome = discord.Client(intents=intents)

bonobo_database.init_database(global_settings['mongoUser'], global_settings['mongoPassword'])

# endregion

# region Global
current_dir = os.path.abspath(os.path.dirname("main.py"))
i = 0
for char in current_dir:
    if char == '\\':
        current_dir = f"{current_dir[0:i]}/{current_dir[i + 1:len(current_dir)]}"
    i += 1

if not(os.path.isdir(f"{current_dir}/local_settings")):
    os.mkdir("local_settings")


async def send_message(message, text, time):
    await asyncio.sleep(0.5)
    await message.channel.purge(limit=1)
    msg = discord.Embed(description=text, colour=discord.colour.Color.gold())
    d_msg = await message.channel.send(embed=msg)
    await asyncio.sleep(time)
    await message.channel.purge(limit=1)
    return d_msg


def settings(guild):
    with open(f"{current_dir}/local_settings/server_guild_{guild.id}/settings.json", "r") as file:
        return json.load(file)


def server(guild):
    return f"{current_dir}/local_settings/server_guild_{guild.id}"

# endregion

# region Events
@client.event
async def on_guild_join(guild):
    print(f"added {guild.name}, id: {guild.id}")
    new_settings = {
            "EconomicUsers": {}
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


# endregion

# region commands
@client.command(name="ping")
async def ping_chek(ctx):
    await send_message(ctx, f"latencia: {round(client.latency * 1000)}ms", 2)


# region Economics
# comando para que un usuario se registre, en este se añade un nuevo elemento al diccionario de usuarios y su cantidad
# de monedas correspondientes que inicia en 0
@client.command(name="register")
async def register(ctx):
    local_settings = settings(ctx.guild)
    if ctx.author.id in local_settings["EconomicUsers"].keys():
        await send_message(ctx, f"ya estas registrado, participa en la economia!", 3)
        return

    local_settings["EconomicUsers"][ctx.author.id] = {
        "coins": 0.0
    }

    json.dump(local_settings, open(f"{server(ctx.guild)}/settings.json", "w"))
    await send_message(ctx, f"has sido añadido a la bonobo-economy {ctx.author.name},tus monedas son 0.0", 3)


# comando para transferir monedas de la wallet del usuario a otro usuario
@client.command(name="send")
async def send_coins(ctx, receptor: discord.member, quantity: float):
    local_settings = settings(ctx.guild)
    economic_users = local_settings["EconomicUsers"]
    if quantity >= 0:
        await send_message(ctx, f"no puedes enviar cantidades negativas o ninguna moneda", 3)
        return

    if not(receptor in economic_users.keys()):
        await send_message(ctx, f"{receptor} no es un usuario registrado", 3)
        return

    if ctx.author.name in economic_users.keys():
        if economic_users[ctx.author.id]["coins"] >= quantity:
            economic_users[ctx.author.name]["coins"] -= quantity
            economic_users[receptor.id]["coins"] += quantity

            tran_bson = {
                "date": str(datetime.datetime.now(pytz.utc)),
                "sender": ctx.author.name,
                "receptor": receptor.name,
                "quantity": quantity
            }

            bonobo_database.send_transaction(tran_bson)

            local_settings["EconomicUsers"] = economic_users
            json.dump(local_settings, open(f"{server(ctx.guild)}/settings.json", "w"))
            await send_message(ctx,
                               f"transaccion completa, quedaste con {economic_users[ctx.author.id]['coins']} monedas"
                               , 3)
        else:
            await send_message(ctx, f"no tienes suficientos monedas", 3)
    else:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings['prefix']}regi", 3)


@client.command(name="coins")
async def get_coins(ctx):
    await send_message(ctx, f"tienes {settings(ctx.guild)['EconomicUsers'][ctx.author.id]['coins']} bonobo coins", 3)


# con este comando se inizializa el forgado de monedas, cada nuevo forgado se le asigna una moneda a un usuario random
# y se guarda un log del diccionario con los usuarios y su cantidad de monedas, estos logs deben ser extraidos del host
# para poder realizar las estadisticas del experimento
@client.command(name="init")
@commands.has_permissions(administrator=True)
async def init_economy(ctx):
    await ctx.channel.purge(limit=1)

#    i = 0
#    for j in os.listdir(f"{server(ctx.guild)}/EconomyLogs"):
#        logn = int(j[4])
#        if logn >= i:
#            i = i + i - logn + 1

    while True:
        local_settings = settings(ctx.guild)
        await asyncio.sleep(2) # Esperar para generar monedas

        economic_users = local_settings['EconomicUsers'] # lee los setings.json del server

        # Toma un usuario al azar para darle una moneda
        rnd = randint(0, len(economic_users.keys()) - 1)
        rnd_user = list(economic_users.keys())[rnd]
        economic_users[rnd_user]["coins"] += 1

        local_settings["EconomicUsers"] = economic_users
        json.dump(local_settings, open(f"{server(ctx.guild)}/settings.json", "w"))

        # Mandar a mongo
        log_users = {}
        for key in economic_users.keys():
            id_user = int(key)
            user = client.get_user(id_user)

            log_users[f"{user.name}_{key}"] = economic_users[key]["coins"]

        log_bson = {
            "date": str(datetime.datetime.now(pytz.utc)),
            "data": log_users # Lo manda como object
        }

        bonobo_database.send_log(log_bson)

#        with open(f"{server(ctx.guild)}/EconomyLogs/log_{i}.txt", "w") as log:
#            log.write(f"{date_string}\n{economic_users}")
        await ctx.channel.send(f"Una nueva moneda se ha forjado, se le ha asignado a {user.name}")
        # i += 1

# endregion

# Output the list of commands available
@client.command(name="help")
async def help_cmd(ctx):
    helpstr = discord.Embed(title=f"Ayuda | MIGALA MONEDAS BOT {client.command_prefix}help", colour=discord.colour.Color.orange())

    helpstr.add_field(
        name=f"{client.command_prefix}regi",
        value="Crea una wallet con el nombre de tu usuario",
    )

    helpstr.add_field(
        name=f"{client.command_prefix}send",
        value="Transfiere bonobo-coins de tu wallet a un usuario\n\nArgumentos: receptor: nombre del usuario receptor;"
              "cantidad: cantidad de bonobo-coins",
    )

    await ctx.channel.purge(limit=1)
    await ctx.send(embed=helpstr)


@client.command()
async def probar(ctx):

    # Ver miembros
    g = ctx.guild.members[0].guild

    for m in g.members:
        print(m)

    print(client.get_user(ctx.author.id))
    print(client.get_user(609202751213404191))
    


# endregion
print("works")
client.run(global_settings["token"])
