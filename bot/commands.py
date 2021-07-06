"""Registra todos los comandos del bot"""

from models.product import Product
from database import db_utils
from models.economy_user import EconomyUser
from discord.ext import commands
from discord.ext.commands import Context, BadArgument

from database.db_utils import *
from utils.utils import get_global_settings
from bot.discord_client import get_client
from bot.bot_utils import *

import core.economy_management
import core.utils
import core.transactions
import core.store
import core.users

from utils.utils import *
from models.enums import ProductStatus, TransactionStatus

client = get_client()
global_settings = get_global_settings()


@client.command(name="stop")
async def stop_bot(ctx: Context):
    """Envia un mensaje con el ping del bot

    Args:
        ctx (Context): Context de discord
    """
    for dev_id in global_settings.dev_ids:
        if dev_id == ctx.author.id:
            await client.logout()
            await client.close()


@client.command(name="ping")
async def ping_chek(ctx: Context):
    """Envia un mensaje con el ping del bot

    Args:
        ctx (Context): Context de discord
    """
    await send_message(ctx, f"latencia: {round(client.latency * 1000)}ms")


@client.command(name="bug")
async def report_bug(ctx: Context, command: str, *, info: str):
    """Reporta un bug a los desarrolladores

    Args:
        ctx (Context): Context de discord
        command (str): Comando que ocaciono el bug
        info (str): Titulo"/"descripcion del bug

    """
    database_name = get_database_name(ctx.guild)
    title_description = key_split(info, "/")

    work_successful, bug = core.utils.report_bug_log(
        ctx.author.id, title_description[0], title_description[1], command, database_name)
    if work_successful:
        for id in global_settings.dev_ids:
            dev = await client.fetch_user(id)
            await dev.send(f"BUG REPORT: {bug.__dict__}")

        await send_message(ctx, "reportado")
        await ctx.author.send("gracias por reportar un bug, intentaremos solucionarlo lo antes posible.\n"
                              "porfavor no reenvie este bug o haga un mal uso del reporte, ya que obstruye el "
                              "trabajo de los desarrolladores")

    else:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings.prefix}registro")


@client.command(name="registro")
async def register(ctx: Context):
    """ Comando para que un usuario se registre, en este se añade un nuevo archivo a la base de datos de balances de
        usuarios y su cantidad de monedas correspondientes que inicia en 0

    Args:
        ctx (Context): Context de discord
    """

    db_name = get_database_name(ctx.guild)
    new_user = EconomyUser(ctx.author.id, db_name,
                           name=ctx.author.name)

    registered = new_user.register()
    if registered:
        await send_message(ctx, f'has sido añadido a la {global_settings.economy_name} {new_user.name}, tienes {new_user.balance} {global_settings.coin_name}')
    else:
        await send_message(ctx, f'{new_user.name} ya estas registrado')


@client.command(name="desregistro")
async def de_register(ctx: Context, *, motive="nulo"):
    """ Comando para que un usuario se des registre, su balance se elimina de la base de datos de Mongo

    Args:
        ctx (Context): Context de discord
        motive (str): Motivo del des registro, por defecto es nulo
    """

    db_name = get_database_name(ctx.guild)
    user = EconomyUser(ctx.author.id, db_name)
    user_exists = user.get_data_from_db()
    if user_exists:
        # TODO: Checar si tiene productos en la tienda
        user.unregister()
        core.utils.send_unregistered_log(user, db_name, motive)
        await send_message(ctx, f'te has des registrado de la {global_settings.economy_name} {user.name}, lamentamos tu des registro')


@client.command(name="transferir")
async def transference(ctx: Context, quantity: float, receptor: discord.Member):
    """Comando para transferir monedas de la wallet del usuario a otro usuario

    Args:
        ctx (Context): Context de discord
        quantity (float): Cantidad a transferir
        receptor (discord.Member): Mención a un usuario de discord
    """
    database_name = get_database_name(ctx.guild)
    channel_name = ctx.message.channel.name

    sender = EconomyUser(ctx.author.id, database_name, name=ctx.author.name, roles=[
        rol.name for rol in ctx.author.roles if rol.name != "@everyone"])

    receptor_t = EconomyUser(receptor.id, database_name, name=receptor.name, roles=[
        rol.name for rol in receptor.roles if rol.name != "@everyone"])

    status, transaction_id = core.transactions.new_transaction(
        sender, receptor_t, quantity, database_name, channel_name)
    if status == TransactionStatus.negative_quantity:
        await send_message(ctx, f"no puedes enviar cantidades negativas o ninguna moneda")
    elif status == TransactionStatus.sender_not_exists:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings.prefix}registro")
    elif status == TransactionStatus.receptor_not_exists:
        await send_message(ctx, f"{receptor.name} no es un usuario registrado")
    elif status == TransactionStatus.sender_is_receptor:
        await send_message(ctx, "no te puedes auto transferir monedas")
    elif status == TransactionStatus.insufficient_coins:
        await send_message(ctx, "no tienes monedas suficientes")
    elif status == TransactionStatus.succesful:
        await send_message(ctx, "transaccion completa")
        await ctx.author.send(f"le transferiste a el usuario {receptor.name}, "
                              f"id {receptor.id}, {quantity} monedas, quedaste con "
                              f"{sender.balance} monedas\nid transaccion: {transaction_id}")

        await receptor.send(f"el usuario {ctx.author.name}, id {ctx.author.id}, te ha transferido {quantity} "
                            f"monedas, has quedado con {receptor_t.balance} monedas\n"
                            f"id transaccion: {transaction_id}")


@client.command(name="monedas")
async def get_coins(ctx: Context):
    """Comando para solicitar un mensaje con la cantidad de monedas que el usuario tiene.

    Args:
        ctx (Context): Context de discord
    """
    database_name = get_database_name(ctx.guild)
    user = EconomyUser(ctx.author.id, database_name)
    exists = user.get_data_from_db()

    if exists:
        await send_message(ctx, f"tienes {user.balance} {global_settings.coin_name} {ctx.author.name}")
    else:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings.prefix}registro")


@client.command(name="producto")
async def sell_product_in_shop(ctx: Context, price: float, *, info: str):
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
    title = name_description[0]
    description = name_description[1]
    database_name = get_database_name(ctx.guild)

    new_product = Product(ctx.author.id, title,
                          description, price, database_name)
    check = new_product.check_info()
    if check == ProductStatus.negative_quantity:
        await send_message(ctx, "el precio no puede ser negativo o 0")
        return
    elif check == ProductStatus.seller_does_not_exist:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings.prefix}registro")
        return

    await ctx.channel.purge(limit=1)

    msg = await send_message(ctx, f"Vendedor: {ctx.author.name}\n{name_description[1]}",
                             f"${price} {name_description[0]}")
    new_product.id = msg.id
    new_product.send_to_db()

    await ctx.author.send(f"tu producto ah sido registrado exitosamente, este es el id del producto: "
                          f"{new_product.id}")
    await msg.add_reaction("🪙")
    await msg.add_reaction("❌")


@client.command(name="editproducto")
async def edit_product_in_shop(ctx: Context, _id, price=0, *, info="0/0"):
    """Comando para editar una interfaz de venta a un producto o servicio, en los argumentos con valor por defecto no se
       haran cambios

    Args:
        ctx (Context): Context de Discord
        _id (str): Id del producto, valor por defecto 0
        price (float): Precio del producto, valor por defecto 0
        info (str): "Título"/"Descripción" del producto, valor por defecto 0
    """

    try:
        price = float(price)
        _id = int(_id)
    except:
        raise BadArgument

    name_description = key_split(info, "/")
    database_name = get_database_name(ctx.guild)
    status = core.store.edit_product(
        _id, ctx.author.id, database_name, price, name_description[0], name_description[1])

    if status == ProductStatus.seller_does_not_exist:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings.prefix}registro", 0, True)
        return
    elif status == ProductStatus.no_exists_in_db:
        await send_message(ctx, f"id invalido", 0, True)
        return
    elif status == ProductStatus.user_is_not_seller_of_product:
        await send_message(ctx, f"No puedes modificar un producto que no es tuyo.")
    elif status == ProductStatus.negative_quantity:
        await send_message(ctx, "el precio no puede ser negativo", 0, True)
        return

    embed = discord.Embed(title=f"${price} {name_description[0]}", description=f"Vendedor: {ctx.author.name}\n"
                                                                               f"{name_description[1]}",
                          colour=discord.colour.Color.orange())

    msg = await ctx.channel.fetch_message(_id)
    await msg.edit(embed=embed)

    await ctx.author.send(f"tu producto ha sido editado exitosamente")
    await send_message(ctx, "editado", 0, True)


@client.command(name="delproducto")
async def del_product_in_shop(ctx: Context, _id: str):
    """Comando para eliminar una interfaz de venta a un producto o servicio

    Args:
        ctx (Context): Context de Discord
        _id (str): Id del producto en la base de datos
    """

    try:
        _id = int(_id)
    except:
        raise BadArgument

    database_name = get_database_name(ctx.guild)
    product, product_exists = Product.from_database(_id, database_name)

    if not product_exists:
        await send_message(ctx, f"id invalido", 0, True)
        return

    balance = query("_id", ctx.author.id, database_name,
                    CollectionNames.users.value)
    if balance is None:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings.prefix}registro", 0, True)
        return

    if product.user_id == ctx.author.id:
        product.delete_on_db()
        msg = await ctx.channel.fetch_message(product.id)
        await ctx.channel.purge(limit=1)
        await msg.delete()
        await ctx.author.send(f"has eliminado tu producto {product.name}")

    elif ctx.author.permissions_in(ctx.channel).administrator is True:
        product.delete_on_db()
        await ctx.channel.purge(limit=1)
        msg = await ctx.channel.fetch_message(product.id)
        await msg.delete()
        seller_user = await client.fetch_user(product.user_id)
        await seller_user.send(f"tu producto {product.title} ah sido eliminado por el administrator "
                               f"{ctx.author.name}, id {ctx.author .id}")

        await ctx.author.send(f"has eliminado el producto {product.title}, del usuario {seller_user.name}, id"
                              f" {seller_user.id}")
    else:
        await send_message(ctx, "no puedes eliminar este producto", 0, True)


@client.command(name="productos")
async def get_products_in_shop(ctx: Context):
    """Comando para buscar todos los productos del usuario

    Args:
        ctx (Context): Context de Discord
    """
    database_name = get_database_name(ctx.guild)
    balance = query("_id", ctx.author.id, database_name,
                    CollectionNames.users.value)
    if balance is None:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings.prefix}registro")
        return

    products = core.store.get_user_products(ctx.author.id, database_name)
    embed = discord.Embed(colour=discord.colour.Color.gold(), title="Productos Encontrados",
                          description=f"tabla de productos del usuario {ctx.author.name}")

    if len(products) == 0:
        embed.add_field(name="Nada", value="ningun producto fue encontrado")

    for product in products:
        embed.add_field(
            name=f"{product.title}",
            value=f"ID:{product.id}, Precio: {product.price}")

    await ctx.channel.send(embed=embed)


@client.command(name="usuario")
async def get_user_by_name(ctx: Context, *, _user: str):
    """Comando para buscar todos los usuarios que empiecen por _user

    Args:
        ctx (Context): Context de Discord
        _user (str): Nombre a buscar
    """

    database_name = get_database_name(ctx.guild)
    if _user.startswith("@"):
        _user = _user[1:len(_user)]

    users = core.users.get_users_starting_with(_user, database_name)
    embed = discord.Embed(colour=discord.colour.Color.gold(), title="Usuarios Encontrados",
                          description=f"tabla de todos los usuarios que inician con el nombre especificado")

    if len(users) == 0:
        embed.add_field(name="Nada", value="ningun usuario fue encontrado")

    for user in users:
        embed.add_field(
            name=f"{user.name}",
            value=f"ID:{user.id}\nmonedas:{user.balance}")

    await ctx.channel.send(embed=embed)


@client.command(name="validar")
async def validate_transaction(ctx: Context, _id: str):
    """Comando para validar una transaccion a travez de su id.

    Args:
        ctx (Context): Context de Discord
        _id (float): Cantidad de monedas a imprimir
    """
    database_name = get_database_name(ctx.guild)
    transaction = query_id(
        _id, database_name, CollectionNames.transactions.value)

    if transaction is None:
        await send_message(ctx, "id invalido")
    else:
        sender_user = await client.fetch_user(transaction["sender_id"])
        receiver_user = await client.fetch_user(transaction["receiver_id"])
        await ctx.channel.purge(limit=1)
        await ctx.author.send(f"transaccion {_id} valida")
        await ctx.author.send(embed=discord.Embed(title=f"${transaction['quantity']}",
                              description=f"enviador: id {sender_user.id} name {sender_user.name}\nreceptor: id "
                              f"{receiver_user.id} name {receiver_user.name}", colour=discord.colour.Color.gold()))


@client.command(name="ayuda")
async def help_cmd(ctx: Context):
    """Retorna la lista de comandos disponibles, Manda un mensaje con la información de los comandos del bot

    Args:
        ctx (Context): Context de Discord
    """
    embed = discord.Embed(title=f"Ayuda | ECONOMY BOT {client.command_prefix}help",
                          colour=discord.colour.Color.orange())

    embed.add_field(
        name=f"{client.command_prefix}registro",
        value="Registra una wallet con el nombre e id de tu usuario",
    )

    embed.add_field(
        name=f"{client.command_prefix}desregistro",
        value="Te desregista eliminando tu wallet",
    )

    embed.add_field(
        name=f"{client.command_prefix}monedas",
        value="Escribe la cantidad de monedas del usuario"
    )

    embed.add_field(
        name=f"{client.command_prefix}usuario",
        value="Escribe el id de los usuarios encontrados a partir del nombre especificado\n\n"
              "Argumentos: nombre: nombre del usuario a busacar (@usuario o usuario)"
    )

    embed.add_field(
        name=f"{client.command_prefix}transferir",
        value=f"Transfiere {global_settings.coin_name} de tu wallet a un usuario\n\n"
              f"Argumentos: cantidad: cantidad de {global_settings.coin_name}; receptor: mencion del usuario receptor;",
    )

    embed.add_field(
        name=f"{client.command_prefix}producto",
        value="""Crea una oferta de un producto en un mensaje, manejando la compra de este a travez de reacciones\n\n"
              "Argumentos: precio: cantidad de monedas; info: nombre"/"description""",
    )

    embed.add_field(
        name=f"{client.command_prefix}editproducto",
        value="""Edita un producto, si se pone 0 en un argumento (excepto id) se dejara el valor previo\n\n"
              "Argumentos: id: id del producto; precio: cantidad de monedas; info: nombre"/"description""",
    )

    embed.add_field(
        name=f"{client.command_prefix}delproducto",
        value="""Elimina un producto\n\n"
              "Argumentos: id: id del producto""",
    )

    embed.add_field(
        name=f"{client.command_prefix}productos",
        value="""Busca tods los productos del usuario"""
    )

    embed.add_field(
        name=f"{client.command_prefix}validar",
        value="Valida una transaccion a travez de su id\n\nArgumentos: _id: identificador de la transaccion",
    )

    embed.add_field(
        name=f"{client.command_prefix}bug",
        value="Reporta un bug a los desarrolladores, uselo moderadamente para no obstruir el reporte de bugs\n\n"
              "Argumentos: comando: comando que ocasiono el bug; info: titulo/descripcion del bug"
    )

    await ctx.send(embed=embed)


@client.command(name="imprimir")
@commands.has_permissions(administrator=True)
async def print_coins(ctx: Context, quantity: float, receptor: discord.Member):
    """Comando que requiere permisos de administrador y sirve para agregar una cantidad de monedas a un usuario.

    Args:
        ctx (Context): Context de Discord
        quantity (float): Cantidad de monedas a imprimir
        receptor_id (str): Mención al usuario receptor de las monedas
    """
    if quantity <= 0:
        await send_message(ctx, f"no puedes imprimir cantidades negativas o ninguna moneda")
        return
    quantity = round(quantity, global_settings.max_decimals)

    database_name = get_database_name(ctx.guild)
    receptor_b = EconomyUser(receptor.id, database_name)
    recipient_is_registered = receptor_b.get_data_from_db()
    if not recipient_is_registered:
        await send_message(ctx, f"{receptor.name} no es un usuario registrado")
        return

    receptor_b.balance += quantity

    await send_message(ctx, f"se imprimieron {quantity}, y se le asignaron a {receptor_b.name}, "
                            f"id {receptor_b._id}")


@client.command(name="expropiar")
@commands.has_permissions(administrator=True)
async def expropriate_coins(ctx: Context, quantity: float, receptor: discord.Member):
    """Comando que requiere permisos de administrador y sirve para quitarle monedas a un usuario

    Args:
        ctx (Context): Context de discord
        quantity (float): Cantidad que se le va a quitar a usuario
        receptor_id (str): Mención al usuario que se le van a quitar monedas
    """

    if quantity <= 0:
        await send_message(ctx, f"no puedes imprimir cantidades negativas o ninguna moneda")
        return
    quantity = round(quantity, global_settings.max_decimals)

    database_name = get_database_name(ctx.guild)
    receptor_b = EconomyUser(receptor.id, database_name)
    recipient_is_registered = receptor_b.get_data_from_db()
    if not recipient_is_registered:
        await send_message(ctx, f"{receptor.name} no es un usuario registrado")
        return

    receptor_b.balance -= quantity

    await send_message(ctx, f"se le expropiaron {quantity} monedas a {receptor_b.name}, "
                            f"id {receptor_b._id}")


@client.command(name="stopforge")
@commands.has_permissions(administrator=True)
async def stopforge(ctx: Context):
    database_name = get_database_name(ctx.guild)
    core.economy_management.stop_forge_coins(database_name)


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

    database_name = get_database_name(ctx.guild)
    users = query_all(database_name, CollectionNames.users.value)
    if users.count() == 0:
        await send_message(ctx, 'No hay usuarios registrados')
        return

    embed = discord.Embed(colour=discord.colour.Color.gold(), title="Tabla de Usuarios",
                          description=f"tabla de todos los usuarios del bot, con su nombre, id y cantidad de monedas")

    for user in users:
        embed.add_field(
            name=f"{user['name']}",
            value=f"ID:{user['_id']}\nmonedas:{user['balance']}")

    # currency_tb = await ctx.channel.send(embed=embed)
    await ctx.channel.send(embed=embed)

    while core.economy_management.forge_coins(database_name):
        # TODO: futuro algoritmo de generacion de monedas
        # Esperar para generar monedas, 900=15min
        await asyncio.sleep(2)

        random_user = db_utils.get_random_user(database_name)
        random_user.balance += 1

        # TODO: Log del forjado (DISCUSION)

        # Pide toda la base de datos y puede ser muy pesado pedirla en cada forjado
        # embed = discord.Embed(colour=discord.colour.Color.gold(), title="Tabla de Usuarios",
        #                       description=f"tabla de todos los usuarios del bot, con su nombre, id y cantidad de monedas")
        # users = query_all(database_name, CollectionNames.users.value)
        # for user in users:
        #     embed.add_field(
        #         name=f"{user['name']}",
        #         value=f"ID:{user['_id']}\nmonedas:{user['balance']}")

        # await currency_tb.edit(embed=embed, content="")

        await send_message(ctx, f"se le ha asignado a {random_user.name}", "Nueva Moneda")


@client.command(name="reset")
@commands.has_permissions(administrator=True)
async def reset_economy(ctx: Context):
    """Pone los balances de todos los usuarios en 0, Requiere permisos de administrador

    Args:
        ctx (Context): Context de Discord
    """
    db_name = get_database_name(ctx.guild)
    core.economy_management.reset_economy(db_name)

    await send_message(ctx, "todos los usuarios tienen 0 monedas")


@client.command(name="adminayuda")
@commands.has_permissions(administrator=True)
async def admin_help_cmd(ctx: Context):
    """Retorna la lista de comandos disponibles para los admins, Manda un mensaje con la información de los comandos del
       bot

    Args:
        ctx (Context): Context de Discord
    """
    embed = discord.Embed(title=f"Ayuda | ECONOMY BOT {client.command_prefix}help",
                          colour=discord.colour.Color.orange())

    embed.add_field(
        name=f"{client.command_prefix}imprimir",
        value="imprime monedas de la nada y se las asigna a un usuario\n\n"
              "Argumentos: cantidad: cantidad de monedas a imprimir; usuario: mencion (@user) ",
    )

    embed.add_field(
        name=f"{client.command_prefix}expropiar",
        value="Le expropia monedas a un usuario\n\n"
              "Argumentos: cantidad: cantidad de monedas a expropiar; usuario: mencion (@user) ",
    )

    embed.add_field(
        name=f"{client.command_prefix}init",
        value="Escribe la cantidad de monedas del usuario"
    )

    embed.add_field(
        name=f"{client.command_prefix}reset",
        value="Escribe el id de los usuarios encontrados a partir del nombre especificado"
    )

    embed.add_field(
        name=f"{client.command_prefix}stopforge",
        value="Detiene el forjado de monedas"
    )

    await ctx.send(embed=embed)
