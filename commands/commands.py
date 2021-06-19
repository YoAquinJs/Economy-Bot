from random import randint, random
from discord.ext import commands

from utils.utils import *
from db import bonobo_database, balances_db, shop_db
from client.client import get_client

client = get_client()

# region commands


@client.command(name="ping")
async def ping_chek(ctx):
    await send_message(ctx, f"latencia: {round(client.latency * 1000)}ms")


# region Economics
# comando para que un usuario se registre, en este se añade un nuevo elemento al diccionario de usuarios y su cantidad
# de monedas correspondientes que inicia en 0
@client.command(name="regis")
async def register(ctx):
    balance = balances_db.get_balance(ctx.author.id, ctx.guild)
    if balance is not None:
        await send_message(ctx, f"{ctx.author.name} ya estas registrado, tienes {balance['balance']} monedas")
        return

    balances_db.create_balance(ctx.author.id, ctx.author.name, 0, ctx.guild)

    await send_message(ctx, f"has sido añadido a la bonobo-economy {ctx.author.name}, tienes 0.0 monedas")


# comando para transferir monedas de la wallet del usuario a otro usuario
@client.command(name="transferir")
async def send_coins(ctx, quantity: float, receptor_id):
    receptor_id = parse_mention_id(receptor_id)

    if quantity <= 0:
        await send_message(ctx, f"no puedes enviar cantidades negativas o ninguna moneda")
        return

    balance_of_sender = balances_db.get_balance(ctx.author.id, ctx.guild)
    balance_of_receptor = balances_db.get_balance(receptor_id, ctx.guild)

    if balance_of_sender is None:
        await send_message(ctx, f"{ctx.author.name} no estas registrado")
        return

    if balance_of_receptor is None:
        await send_message(ctx, f"{receptor_id} no es un usuario registrado")
        return

    if receptor_id == ctx.author.id:
        await send_message(ctx, "no te puedes auto transferir monedas")
        return

    if balance_of_sender['balance'] < quantity:
        await send_message(ctx, "no tienes monedas suficientes")
        return

    # Se hace la transaccion
    balance_of_sender['balance'] -= quantity
    balance_of_receptor['balance'] += quantity
    # Se manda hace cambio de saldos en la db
    balances_db.modify_balance(
        balance_of_receptor['user_id'], balance_of_receptor['balance'], ctx.guild)
    balances_db.modify_balance(
        balance_of_sender['user_id'], balance_of_sender['balance'], ctx.guild)

    sender = {
        "id": balance_of_sender['user_id'],
        "roles": [rol.name for rol in ctx.author.roles if rol.name != "@everyone"]
    }

    fetch_receptor = ctx.guild.get_member(balance_of_receptor['user_id'])
    receptor = {
        "id": balance_of_receptor['user_id'],
        "roles": [rol.name for rol in fetch_receptor.roles if rol.name != "@everyone"]
    }

    transacition_log = {
        "date": get_time(),
        "type": "transferencia",
                "sender": sender,
                "receptor": receptor,
                "quantity": quantity,
                "channel_name": ctx.message.channel.name
    }
    bonobo_database.send_transaction(transacition_log, ctx.guild)

    await send_message(ctx, "transaccion completa", 2)
    await ctx.author.send(f"le transferiste a el usuario {balance_of_receptor['user_name']}, id {balance_of_receptor['user_id']}, {quantity} "
                          f"monedas, quedaste con {balance_of_sender['balance']} monedas")
    await fetch_receptor.send(f"el usuario {ctx.author.name}, id {ctx.author.id}, te ha transferido {quantity} "
                              f"monedas, has quedado con {balance_of_receptor['balance']} monedas")


@client.command(name="monedas")
async def get_coins(ctx):
    balance = balances_db.get_balance(ctx.author.id, ctx.guild)
    if balance is None:
        await send_message(ctx, f"{ctx.author.name} no estas registrado, utiliza el comando {client.get_prefix()}regis")
        return

    await send_message(ctx, f"tienes {balance['balance']} bonobo coins {ctx.author.name}")


@client.command(name="imprimir")
@commands.has_permissions(administrator=True)
async def print_coins(ctx, quantity: float, receptor_id: str):
    receptor_id = parse_mention_id(receptor_id)

    receptor = balances_db.get_balance(receptor_id, ctx.guild)
    receptor['balance'] += quantity
    balances_db.modify_balance(
        receptor['user_id'], receptor['balance'], ctx.guild)

    await send_message(ctx, f"se imprimieron {quantity}, y se le asignaron a {receptor['user_name']}, id {receptor['user_id']}")


@client.command(name="expropiar")
@commands.has_permissions(administrator=True)
async def expropriate_coins(ctx, quantity: float, receptor_id: str):
    receptor_id = parse_mention_id(receptor_id)

    receptor = balances_db.get_balance(receptor_id, ctx.guild)
    if receptor['balance'] < quantity:
        quantity = receptor['balance']
        receptor['balance'] = 0
    else:
        receptor['balance'] -= quantity

    balances_db.modify_balance(
        receptor['user_id'], receptor['balance'], ctx.guild)

    await send_message(ctx, f"se le expropiaron {quantity} monedas a {receptor['user_name']}, id {receptor['user_id']}")


# con este comando se inizializa el forgado de monedas, cada nuevo forgado se le asigna una moneda a un usuario random
# y se guarda un log del diccionario con los usuarios y su cantidad de monedas, estos logs deben ser extraidos del host
# para poder realizar las estadisticas del experimento
@client.command(name="init")
@commands.has_permissions(administrator=True)
async def init_economy(ctx):
    await ctx.channel.purge(limit=1)
    currency_tb = await ctx.channel.send("_")
    users = balances_db.get_balances_cursor(ctx.guild)

    embed = discord.Embed(colour=discord.colour.Color.gold(), title="Tabla de Usuarios",
                          description=f"tabla de todos los usuarios del bot, con su nombre, id y cantidad de monedas")

    for user in users:
        embed.add_field(
            name=f"{user['user_name']}",
            value=f"ID:{user['user_id']}\nmonedas:{user['balance']}")

    await currency_tb.edit(embed=embed, content="")

    while True:
        await asyncio.sleep(10)  # Esperar para generar monedas, 900=15min

        embed = discord.Embed(colour=discord.colour.Color.gold(), title="Tabla de Usuarios",
                              description=f"tabla de todos los usuarios del bot, con su nombre, id y cantidad de monedas")

        for user in users:
            embed.add_field(
                name=f"{user['user_name']}",
                value=f"ID:{user['user_id']}\nmonedas:{user['balance']}")

        await currency_tb.edit(embed=embed, content="")

        random_user = bonobo_database.get_random_user(ctx.guild)
        random_user['balance'] += 1
        balances_db.modify_balance(
            random_user['user_id'], random_user['balance'], ctx.guild)

        log_bson = {
            "date": get_time(),
            "data": {
                'type': 'forjado',
                'user_id': random_user['user_id'],
                'user_name': random_user['user_name']
            }  # Lo manda como object
        }
        bonobo_database.send_log(log_bson, ctx.guild)

        embed = discord.Embed(description=f"se le ha asignado a {random_user['user_name']}",
                              colour=discord.colour.Color.gold(), title="Nueva Moneda")
        await ctx.channel.send(embed=embed)
        # i += 1


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
    pass


@client.command(name="vender")
async def sell_in_shop(ctx, price: float, *, info: str):
    if len(info) == 0:
        await send_message(ctx, "tienes que ingresar un nombre")
        return
    i = 0
    for ch in info:
        if ch == "/":
            name = info[0:i]
            description = info[i+1:len(info)]
            break
        i += 1

    if price <= 0:
        await send_message(ctx, "el precio no puede ser negativo o 0")
        return

    balance_user = balances_db.get_balance(ctx.author.id, ctx.guild)
    if balance_user is None:
        await send_message(ctx, f"no estas registrado, registrate con {client.command_prefix}regis")
        return

    await ctx.channel.purge(limit=1)
    embed = discord.Embed(colour=discord.colour.Color.orange(), title=f"${price} {name}",
                          description=f"Vendedor:{ctx.author.name}\n{description}")
    msg = await ctx.channel.send(embed=embed)

    product = {
        "msg_id": msg.id,
        "Price": price,
        "Name": name,
        "UserID": ctx.author.id
    }

    shop_db.save_product(product, ctx.guild)

    await msg.add_reaction("🪙")
    await msg.add_reaction("❌")
# for buy in on_raw_reaction_add


@client.command(name="usuario")
async def get_user_by_name(ctx, *, user: str):
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
            key_values = key_split(key)

            embed.add_field(
                name=f"{key_values[0]}",
                value=f"ID:{key_values[1]}\nmonedas:{economic_users[key]['coins']}")

    if user_founds == 0:
        user_founds += 1
        embed.add_field(name="ninguno")

    await ctx.channel.send(embed=embed)
    await asyncio.sleep(user_founds * 3)
    await ctx.channel.purge(limit=1)


@client.command(name="reset")
@commands.has_permissions(administrator=True)
async def reset_economy(ctx):

    users = balances_db.get_balances_cursor(ctx.guild)
    for user in users:
        balances_db.modify_balance(user['user_id'], 0, ctx.guild)

    await send_message(ctx, "economia desde 0, todos los usuarios tienen 0 monedas")
