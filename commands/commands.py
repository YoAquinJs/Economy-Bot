import datetime
import pytz
from discord.ext import commands
from random import randint

from client.client import client
from utils.utils import *
from db import bonobo_database

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
        await send_message(ctx, f"no estas registrado, registrate con {client.command_prefix}regi", 3)


@client.command(name="monedas")
async def get_coins(ctx):
    economic_users = settings(ctx.guild)["EconomicUsers"]
    await send_message(ctx, f"tienes {economic_users[f'{ctx.author.name}_{str(ctx.author.id)}']['coins']} bonobo coins", 3)


@client.command(name="usuario")
async def get_user_by_name(ctx, *, user):
    await ctx.channel.purge(limit=1)
    economic_users = settings(ctx.guild)["EconomicUsers"]
    user_founds = 0

    if user.startswith("@"):
        user = user[1:len(user)]

    embed = discord.Embed(colour=discord.colour.Color.gold(), title="Usuarios Encontrados",
                          description=f"tabla de todos los usuarios que inician con el nombre especificado")

    for key in economic_users.keys():
        if key.casefold().startswith(user.casefold()):
            user_founds += 1
            i = 0

            for ch in key:
                if ch == "_":
                    break
                i = i + 1

            embed.add_field(
                name=f"{key[0:i]}",
                value=f"ID:{key[i + 1:len(key)]}\nmonedas:{economic_users[key]['coins']}")

    if user_founds == 0:
        user_founds += 1
        embed.add_field(name="ninguno")
    await ctx.channel.send(embed=embed)
    await asyncio.sleep(user_founds * 3)
    await ctx.channel.purge(limit=1)


@client.command(name="reset")
@commands.has_permissions(administrator=True)
async def reset_economy(ctx):
    local_settings = settings(ctx.guild)
    economic_users = local_settings["EconomicUsers"]

    for key in economic_users.keys():
        economic_users[key]["coins"] = 0

    local_settings["EconomicUsers"] = economic_users
    json.dump(local_settings, open(f"{server(ctx.guild)}/settings.json", "w"))

    await send_message(ctx, "economia desde 0, todos los usuarios tienen 0 monedas", 3)


# con este comando se inizializa el forgado de monedas, cada nuevo forgado se le asigna una moneda a un usuario random
# y se guarda un log del diccionario con los usuarios y su cantidad de monedas, estos logs deben ser extraidos del host
# para poder realizar las estadisticas del experimento
@client.command(name="init")
@commands.has_permissions(administrator=True)
async def init_economy(ctx):
    await ctx.channel.purge(limit=1)
    local_settings = settings(ctx.guild)
    economic_users = local_settings['EconomicUsers']  # lee los setings.json del server
    currency_tb = await ctx.channel.send("_")

    while True:
        embed = discord.Embed(colour=discord.colour.Color.gold(), title="Tabla de Usuarios",
                              description=f"tabla de todos los usuarios del bot, con su nombre, id y cantidad de monedas")

        for key in economic_users.keys():
            i = 0
            for ch in key:
                if ch == "_":
                    break
                i = i + 1

            embed.add_field(
                name=f"{key[0:i]}",
                value=f"ID:{key[i + 1:len(key)]}\nmonedas:{economic_users[key]['coins']}")
        await currency_tb.edit(embed=embed, content="")

        await asyncio.sleep(5) # Esperar para generar monedas, 900=15min

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
    embed = discord.Embed(title=f"Ayuda | MIGALA MONEDAS BOT {client.command_prefix}help",
                          colour=discord.colour.Color.orange())

    embed.add_field(
        name=f"{client.command_prefix}regis",
        value="Crea una wallet con el nombre de tu usuario",
    )

    embed.add_field(
        name=f"{client.command_prefix}monedas",
        value="Escribe la cantidad de monedas del usuario"
    )

    embed.add_field(
        name=f"{client.command_prefix}usuario",
        value="Escribe el id de los usuarios encontrados a partir del nombre especificado\n\nArgumentos: nombre: nombre"
              " del usuario a busacar (@usuario o usuario)"
    )

    embed.add_field(
        name=f"{client.command_prefix}enviar",
        value="Transfiere bonobo-coins de tu wallet a un usuario\n\nArgumentos: receptor: id del usuario receptor;"
              "cantidad: cantidad de bonobo-coins",
    )

    await ctx.channel.purge(limit=1)
    await ctx.send(embed=embed)


@client.command()
async def probar(ctx):

    # Ver miembros
    g = ctx.guild.members[0].guild

    for m in g.members:
        print(m)

    print(client.get_user(ctx.author.id))
    print(client.get_user(609202751213404191))