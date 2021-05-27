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

bonobo_database.init_database(global_settings['mongoUser'], global_settings['mongoPassword'])

# endregion

# region ServerGlobal
# se aplica para todo el codigo y mas especifico cada server
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
@client.command(name="regis")
async def register(ctx):
    local_settings = settings(ctx.guild)
    if ctx.author.id in local_settings["EconomicUsers"].keys():
        await send_message(ctx, f"ya estas registrado, participa en la economia!", 3)
        return

    local_settings["EconomicUsers"][f"{ctx.author.name}_{ctx.author.id}"] = {
        "coins": 0.0
    }

    json.dump(local_settings, open(f"{server(ctx.guild)}/settings.json", "w"))
    await send_message(ctx, f"has sido añadido a la bonobo-economy {ctx.author.name}, tienes 0.0 monedas", 3)


# comando para transferir monedas de la wallet del usuario a otro usuario
@client.command(name="transferir")
async def send_coins(ctx, receptor_id, quantity: float):
    local_settings = settings(ctx.guild)
    economic_users = local_settings["EconomicUsers"]
    receptor = await client.fetch_user(receptor_id)
    receptor_key = f"{receptor.name}_{receptor_id}"
    author_key = f"{ctx.author.name}_{ctx.author.id}"

    if quantity <= 0:
        await send_message(ctx, f"no puedes enviar cantidades negativas o ninguna moneda", 3)
        return

    if not(receptor_key in economic_users.keys()):
        await send_message(ctx, f"{receptor_key} no es un usuario registrado", 3)
        return

    if author_key in economic_users.keys():
        if economic_users[author_key]["coins"] >= quantity:
            economic_users[author_key]["coins"] -= quantity
            economic_users[receptor_key]["coins"] += quantity

            tran_bson = {
                "date": str(datetime.datetime.now(pytz.utc)),
                "sender": author_key,
                "receptor": receptor_key,
                "quantity": quantity
            }

            bonobo_database.send_transaction(tran_bson)

            local_settings["EconomicUsers"] = economic_users
            json.dump(local_settings, open(f"{server(ctx.guild)}/settings.json", "w"))
            await send_message(ctx,
                               f"transaccion completa, quedaste con {economic_users[author_key]['coins']} monedas"
                               , 3)
        else:
            await send_message(ctx, f"no tienes suficientos monedas", 3)
    else:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings['prefix']}regi", 3)


@client.command(name="monedas")
async def get_coins(ctx):
    economic_users = settings(ctx.guild)["EconomicUsers"]
    await send_message(ctx, f"tienes {economic_users[f'{ctx.author.name}_{str(ctx.author.id)}']['coins']} bonobo coins", 3)


@client.command(name="usuario")
async def get_id_by_name(ctx, *, user):
    economic_users = settings(ctx.guild)["EconomicUsers"]
    msg = "Usuarios encontrados:\n"
    user_founds = 0

    if user.startswith("@"):
        user = user[1:len(user)]
    for key in economic_users.keys():
        if key.casefold().startswith(user.casefold()):
            user_founds += 1
            i = 0

            for ch in key:
                if ch == "_":
                    break
                i = i + 1

            msg = f"{msg}usuario:{key[0:i]}; id:{key[i+2:len(key)]}\n"

    if user_founds == 0:
        user_founds += 1
        msg = f"{msg}ninguno."
    await send_message(ctx, msg, user_founds * 3)


# con este comando se inizializa el forgado de monedas, cada nuevo forgado se le asigna una moneda a un usuario random
# y se guarda un log del diccionario con los usuarios y su cantidad de monedas, estos logs deben ser extraidos del host
# para poder realizar las estadisticas del experimento
@client.command(name="init")
@commands.has_permissions(administrator=True)
async def init_economy(ctx):
    await ctx.channel.purge(limit=1)

    while True:
        local_settings = settings(ctx.guild)
        await asyncio.sleep(5) # Esperar para generar monedas, 900=15min

        economic_users = local_settings['EconomicUsers'] # lee los setings.json del server

        # Toma un usuario al azar para darle una moneda
        rnd = randint(0, len(economic_users.keys()) - 1)
        rnd_user = list(economic_users.keys())[rnd]
        economic_users[rnd_user]["coins"] += 1

        local_settings["EconomicUsers"] = economic_users
        json.dump(local_settings, open(f"{server(ctx.guild)}/settings.json", "w"))

        log_bson = {
            "date": str(datetime.datetime.now(pytz.utc)),
            "data": economic_users # Lo manda como object
        }
        bonobo_database.send_log(log_bson)

        i = 0
        for ch in rnd_user:
            if ch == "_":
                break
            i = i + 1

        embed = discord.Embed(description=f"se le ha asignado a {rnd_user[0:i]}",
                              colour=discord.colour.Color.gold(), title="Nueva Moneda")
        await ctx.channel.send(embed=embed)
        # i += 1

# endregion

# Output the list of commands available
@client.command(name="help")
async def help_cmd(ctx):
    helpstr = discord.Embed(title=f"Ayuda | MIGALA MONEDAS BOT {client.command_prefix}help", colour=discord.colour.Color.orange())

    helpstr.add_field(
        name=f"{client.command_prefix}regis",
        value="Crea una wallet con el nombre de tu usuario",
    )

    helpstr.add_field(
        name=f"{client.command_prefix}monedas",
        value="Escribe la cantidad de monedas del usuario"
    )

    helpstr.add_field(
        name=f"{client.command_prefix}usuario",
        value="Escribe el id de los usuarios encontrados a partir del nombre especificado\n\nArgumentos: nombre: nombre del usuario a busacar (@usuario o usuario)"
    )

    helpstr.add_field(
        name=f"{client.command_prefix}transferir",
        value="Transfiere bonobo-coins de tu wallet a un usuario\n\nArgumentos: receptor: id del usuario receptor;"
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
client.run(global_settings["token"])

# anaconda commands
# cd documents\codeprojects\economy-bot\economy-bot
# conda activate bonoboenv
# python main.py