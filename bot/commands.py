"""Registra todos los comandos del bot"""

from discord.ext import commands
from discord.ext.commands import Context

from database.db_utils import *
from bot.discord_client.discord_client import get_client
from bot.bot_utils import *

client = get_client()
global_settings = get_global_settings()


@client.command(name="ping")
async def ping_chek(ctx: Context):
    """Envia un mensaje con el ping del bot

    Args:
        ctx (Context): Context de discord
    """
    await send_message(ctx, f"latencia: {round(client.latency * 1000)}ms")


@client.command(name="registro")
async def register(ctx: Context):
    """ Comando para que un usuario se registre, en este se añade un nuevo archivo a la base de datos de balances de
        usuarios y su cantidad de monedas correspondientes que inicia en 0

    Args:
        ctx (Context): Context de discord
    """

    balance = query("user_id", ctx.author.id, ctx.guild, Collection.balances.value)

    if balance is not None:
        await send_message(ctx, f"{ctx.author.name} ya estas registrado")
        return

    balance = {
        'user_id': ctx.author.id,
        'user_name': ctx.author.name,
        'balance': 0
    }

    insert(balance, ctx.guild)

    await send_message(ctx, f"has sido añadido a la bonobo-economy {ctx.author.name}, tienes 0.0 monedas")


@client.command(name="transferir")
async def transference(ctx: Context, quantity: float, receptor: discord.Member):
    """Comando para transferir monedas de la wallet del usuario a otro usuario

    Args:
        ctx (Context): Context de discord
        quantity (float): Cantidad a transferir
        receptor (discord.Member): Mención a un usuario de discord
    """

    if quantity <= 0:
        await send_message(ctx, f"no puedes enviar cantidades negativas o ninguna moneda")
        return

    sender_balance = query("user_id", ctx.author.id, ctx.guild, Collection.balances.value)
    receptor_balance = query("user_id", receptor.id, ctx.guild, Collection.balances.value)

    if sender_balance is None:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings['prefix']}registro")
        return

    if receptor_balance is None:
        await send_message(ctx, f"{receptor.name} no es un usuario registrado")
        return

    if receptor.id == ctx.author.id:
        await send_message(ctx, "no te puedes auto transferir monedas")
        return

    if sender_balance['balance'] < quantity:
        await send_message(ctx, "no tienes monedas suficientes")
        return

    # Se hace la transaccion
    sender_balance['balance'] -= quantity
    receptor_balance['balance'] += quantity
    # Se manda hace cambio de saldos en la db
    modify("user_id", receptor_balance['user_id'], "balance", receptor_balance['balance'], ctx.guild,
           Collection.balances.value)
    modify("user_id", sender_balance['user_id'], "balance", sender_balance['balance'], ctx.guild,
           Collection.balances.value)

    transaction_log = {
        "date": get_time(),
        "type": "transferencia",
        "sender": {
            "id": sender_balance['user_id'],
            "roles": [rol.name for rol in ctx.author.roles if rol.name != "@everyone"]
        },
        "receptor": {
            "id": receptor_balance['user_id'],
            "roles": [rol.name for rol in receptor.roles if rol.name != "@everyone"]
        },
        "quantity": quantity,
        "channel_name": ctx.message.channel.name
    }

    transaction = insert(transaction_log, ctx.guild, Collection.transactions.value)

    await send_message(ctx, "transaccion completa")
    await ctx.author.send(f"le transferiste a el usuario {receptor_balance['user_name']}, "
                          f"id {receptor_balance['user_id']}, {quantity} monedas, quedaste con "
                          f"{sender_balance['balance']} monedas\nid transaccion: {transaction.inserted_id}")

    await receptor.send(f"el usuario {ctx.author.name}, id {ctx.author.id}, te ha transferido {quantity} "
                        f"monedas, has quedado con {receptor_balance['balance']} monedas\n"
                        f"id transaccion: {transaction.inserted_id}")


@client.command(name="monedas")
async def get_coins(ctx: Context):
    """Comando para solicitar un mensaje con la cantidad de monedas que el usuario tiene.

    Args:
        ctx (Context): Context de discord
    """

    balance = query("msg_id", ctx.author.id, ctx.guild, Collection.balances.value)

    if balance is None:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings['prefix']}registro")
        return

    await send_message(ctx, f"tienes {balance['balance']} bonobo coins {ctx.author.name}")


@client.command(name="vender")
async def sell_in_shop(ctx: Context, price: float, *, info: str):
    """Comando para crear una interfaz de venta a un producto o servicio

    Args:
        ctx (Context): Context de Discord
        price (float): Precio del producto
        info (str): "Título"/"Descripción" del producto
    """

    if len(info) == 0:
        await send_message(ctx, "tienes que ingresar un nombre")
        return

    name_description = key_split(info, "/")

    if price <= 0:
        await send_message(ctx, "el precio no puede ser negativo o 0")
        return

    balance_user = query("user_id", ctx.author.id, ctx.guild, Collection.balances.value)

    if balance_user is None:
        await send_message(ctx, f"no estas registrado, registrate con {client.command_prefix}regis")
        return

    await ctx.channel.purge(limit=1)

    msg = await send_message(ctx, f"Vendedor:{ctx.author.name}\n{name_description[1]}",
                             f"${price} {name_description[0]}")
    product = {
        "msg_id": msg.id,
        "Price": price,
        "Name": name_description[0],
        "UserID": ctx.author.id
    }

    insert(product, ctx.guild, Collection.shop.value)

    await msg.add_reaction("🪙")
    await msg.add_reaction("❌")


# TODO convert to db
@client.command(name="usuario")
async def get_user_by_name(ctx: Context, *, _user: str):
    await ctx.channel.purge(limit=1)
    users = query_all(ctx.guild, Collection.balances.value)
    user_founds = 0

    if _user.startswith("@"):
        _user = _user[1:len(_user)]

    embed = discord.Embed(colour=discord.colour.Color.gold(), title="Usuarios Encontrados",
                          description=f"tabla de todos los usuarios que inician con el nombre especificado")

    for user in users:
        if user["user_name"].casefold().startswith(_user.casefold()):
            user_founds += 1

            embed.add_field(
                name=f"{user['user_name']}",
                value=f"ID:{user['user_id']}\nmonedas:{user['balance']}")

    if user_founds == 0:
        user_founds += 1
        embed.add_field(name="ninguno")

    await ctx.channel.send(embed=embed)


@client.command(name="imprimir")
@commands.has_permissions(administrator=True)
async def print_coins(ctx: Context, quantity: float, receptor: discord.Member):
    """Comando que requiere permisos de administrador y sirve para agregar una cantidad de monedas a un usuario.

    Args:
        ctx (Context): Context de Discord
        quantity (float): Cantidad de monedas a imprimir
        receptor_id (str): Mención al usuario receptor de las monedas
    """

    receptor_balance = query("user_id", receptor.id, ctx.guild, Collection.balances.value)

    if receptor_balance is None:
        await send_message(ctx, f"{receptor.name} no es un usuario registrado")
        return

    receptor_balance['balance'] += quantity
    modify("user_id", receptor.id, "balance", receptor_balance['balance'], ctx.guild, Collection.balances.value)

    await send_message(ctx, f"se imprimieron {quantity}, y se le asignaron a {receptor_balance['user_name']}, "
                            f"id {receptor_balance['user_id']}")


@client.command(name="expropiar")
@commands.has_permissions(administrator=True)
async def expropriate_coins(ctx: Context, quantity: float, receptor: discord.Member):
    """Comando que requiere permisos de administrador y sirve para quitarle monedas a un usuario

    Args:
        ctx (Context): Context de discord
        quantity (float): Cantidad que se le va a quitar a usuario
        receptor_id (str): Mención al usuario que se le van a quitar monedas
    """

    receptor_balance = query("user_id", receptor.id, ctx.guild, Collection.balances.value)

    if receptor_balance is None:
        await send_message(ctx, f"{receptor.name} no es un usuario registrado")
        return

    if receptor_balance['balance'] < quantity:
        quantity = receptor_balance['balance']
        receptor_balance['balance'] = 0
    else:
        receptor_balance['balance'] -= quantity

    modify("user_id", receptor.id, "balance", receptor_balance['balance'], ctx.guild, Collection.balances.value)

    await send_message(ctx, f"se le expropiaron {quantity} monedas a {receptor_balance['user_name']}, "
                            f"id {receptor_balance['user_id']}")


# TODO refresh db
@client.command(name="init")
@commands.has_permissions(administrator=True)
async def init_economy(ctx: Context):
    """Con este comando se inizializa el forgado de monedas, cada nuevo forgado se le asigna una moneda a un usuario
        random y se guarda un log del diccionario con los usuarios y su cantidad de monedas en la base de datos, estos
        logs deben ser extraidos del host para poder realizar las estadisticas del experimento
    Args:
        ctx (Context): Context de Discord
    """

    await ctx.channel.purge(limit=1)
    currency_tb = await ctx.channel.send("_")
    users = query_all(ctx.guild, Collection.balances.value)

    embed = discord.Embed(colour=discord.colour.Color.gold(), title="Tabla de Usuarios",
                          description=f"tabla de todos los usuarios del bot, con su nombre, id y cantidad de monedas")

    for user in users:
        embed.add_field(
            name=f"{user['user_name']}",
            value=f"ID:{user['user_id']}\nmonedas:{user['balance']}")

    await currency_tb.edit(embed=embed, content="")

    while True:
        # futuro algoritmo de generacion de monedas
        await asyncio.sleep(10)  # Esperar para generar monedas, 900=15min

        embed = discord.Embed(colour=discord.colour.Color.gold(), title="Tabla de Usuarios",
                              description=f"tabla de todos los usuarios del bot, con su nombre, id y cantidad de monedas")

        for user in users:
            embed.add_field(
                name=f"{user['user_name']}",
                value=f"ID:{user['user_id']}\nmonedas:{user['balance']}")

        await currency_tb.edit(embed=embed, content="")

        random_user = get_random_user(ctx.guild)
        random_user['balance'] += 1
        modify("user_id", random_user['user_id'], "balance", random_user['balance'], ctx.guild,
               Collection.balances.value)

        log_bson = {
            "date": get_time(),
            "data": {
                'type': 'forjado',
                'user_id': random_user['user_id'],
                'user_name': random_user['user_name']
            }
        }

        insert(log_bson, ctx.guild, Collection.transactions.value)

        await send_message(ctx, f"se le ha asignado a {random_user['user_name']}", "Nueva Moneda")


@client.command(name="reset")
@commands.has_permissions(administrator=True)
async def reset_economy(ctx: Context):
    """Pone los balances de todos los usuarios en 0, Requiere permisos de administrador

    Args:
        ctx (Context): Context de Discord
    """

    users = query_all(ctx.guild, Collection.balances.value)
    for user in users:
        modify("msg_id", user['user_id'], 0, ctx.guild, Collection.balances.value)

    await send_message(ctx, "todos los usuarios tienen 0 monedas")


@client.command(name="help")
async def help_cmd(ctx: Context):
    """Retorna la lista de comandos disponibles, Manda un mensaje con la información de los comandos del bot

    Args:
        ctx (Context): Context de Discord
    """
    embed = discord.Embed(title=f"Ayuda | MIGALA MONEDAS BOT {client.command_prefix}help",
                          colour=discord.colour.Color.orange())

    embed.add_field(
        name=f"{client.command_prefix}registro",
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
        name=f"{client.command_prefix}transferir",
        value="Transfiere bonobo-coins de tu wallet a un usuario\n\nArgumentos: cantidad: cantidad de bonobo-coins;"
              "receptor: mencion del usuario receptor;",
    )

    embed.add_field(
        name=f"{client.command_prefix}bug",
        value="Reporta un bug a los desarrolladores, porfavor usar con regulacion y sin obstruir el reporte errores"
              "\n\nArgumentos: comando: comando que ocasiono el bug;"
              "info: titulo/descripcion del bug"
    )

    await ctx.channel.purge(limit=1)
    await ctx.send(embed=embed)
