"""Registra todos los comandos del bot"""
import discord

from models.product import Product
from database import db_utils
from models.economy_user import EconomyUser
from discord.ext import commands
from discord.ext.commands import Context, BadArgument
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option


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
slash = SlashCommand(client, sync_commands=True)
guild_ids = [864333042842599444]
global_settings = get_global_settings()


@client.command(name="stop")
async def stop_bot(ctx: Context):
    """Envia un mensaje con el ping del bot

    Args:
        ctx (Context): Context de discord
    """
    for dev_id in global_settings.dev_ids:
        if dev_id == ctx.author.id:
            await client.close()


@client.command(name="ping")
async def ping_chek(ctx: Context):
    """Envia un mensaje con el ping del bot

    Args:
        ctx (Context): Context de discord
    """
    await send_message(ctx, f"Latencia: {int(round(client.latency * 1000, 0))}ms")


@slash.slash(name="bug", guild_ids=guild_ids, description="reporta un bug del bot a los desarrolladores",
             options=[
              create_option(name="comando", description="nombre del comando o sistema que ocasiono el bug",
                            option_type=3, required=True),
              create_option(name="informacion", description="descripcion o detalles del bug",
                            option_type=3, required=True)],
             connector={"comando": "command", "informacion": "info"})
async def report_bug(ctx: SlashContext, command: str, info: str):
    """Reporta un bug a los desarrolladores

    Args:
        ctx (SlashContext): Context de discord
        command (str): Comando que ocaciono el bug
        info (str): Titulo"/"descripcion del bug

    """
    await ctx.defer()

    database_name = get_database_name(ctx.guild)

    work_successful, bug = core.utils.report_bug_log(
        ctx.author.id, info, command, database_name)
    if work_successful:
        for dev_id in global_settings.dev_ids:
            dev = await client.fetch_user(dev_id)
            await dev.send(f"BUG REPORT: {bug.__dict__}, User_ID: {ctx.author.id}")

        await ctx.send("reportado")
        await ctx.author.send("Gracias por reportar un bug, intentaremos solucionarlo lo antes posible.\n"
                              "Por favor no reenvíe este bug o haga un mal uso del reporte, recuerde "
                              "que los desarrolladores también somos personas.")

    else:
        await ctx.send(f"Usuario no registrado. Registrate con {global_settings.prefix}registro")


@slash.slash(name="registro", guild_ids=guild_ids, description=f"Registra una wallet con el nombre e id de tu usuario")
async def register(ctx: SlashContext):
    """ Comando para que un usuario se registre, en este se añade un nuevo archivo a la base de datos de balances de
        usuarios y su cantidad de monedas correspondientes que inicia en 0

    Args:
        ctx (SlashContext): Context de discord
    """
    await ctx.defer()

    db_name = get_database_name(ctx.guild)
    new_user = EconomyUser(ctx.author.id, db_name,
                           name=ctx.author.name)

    registered = new_user.register()
    if registered:
        await ctx.send(f'Has sido añadido a la {global_settings.economy_name} {new_user.name}, tienes '
                       f'{global_settings.initial_number_of_coins} {global_settings.coin_name}')
    else:
        await ctx.send(f'{new_user.name} ya estas registrado')


@slash.slash(name="desregistro", guild_ids=guild_ids, description=f"Elimina del registro al usuario",
             options=[
              create_option(name="motivo", description="motivo del desregistro", option_type=3, required=False)],
             connector={"motivo": "motive"})
async def de_register(ctx: SlashContext, motive="nulo"):
    """ Comando para que un usuario se des registre, su balance se elimina de la base de datos de Mongo

    Args:
        ctx (SlashContext): Context de discord
        motive (str): Motivo del des registro, por defecto es nulo
    """
    await ctx.defer()

    db_name = get_database_name(ctx.guild)
    user = EconomyUser(ctx.author.id, db_name)

    if user.user_exists():
        database_name = get_database_name(ctx.guild)
        products = core.store.get_user_products(ctx.author.id, database_name)

        if len(products) == 0:
            user.unregister()
            core.utils.send_unregistered_log(user, db_name, motive)
            await ctx.send(f'{user.name} has salido de la {global_settings.economy_name}, lamentamos tu partida')
        else:
            await ctx.send(f'El usuario posee productos, primero elimina todos tus productos')
    else:
        await ctx.send(f'Usuario no registrado. Registrate con {global_settings.prefix}registro.')


@slash.slash(name="transferir", guild_ids=guild_ids, description=f"Transfiere {global_settings.coin_name} de tu wallet a un usuario",
             options=[
              create_option(name="cantidad", description=f"cantidad de {global_settings.coin_name}",
                            option_type=3, required=True),
              create_option(name="receptor", description="mencion del usuario receptorr",
                            option_type=6, required=True)],
             connector={"cantidad": "quantity", "receptor": "receptor"})
async def transference(ctx: SlashContext, quantity, receptor: discord.Member):
    """Comando para transferir monedas de la wallet del usuario a otro usuario

    Args:
        ctx (SlashContext): Context de discord
        quantity (float): Cantidad a transferir
        receptor (discord.Member): Mención a un usuario de discord
    """
    await ctx.defer()

    try:
        quantity = round(float(quantity), global_settings.max_decimals)
    except:
        raise BadArgument

    database_name = get_database_name(ctx.guild)
    channel_name = discord.utils.get(client.get_guild(ctx.guild_id).channels, id=ctx.channel_id).name

    sender = EconomyUser(ctx.author.id, database_name, name=ctx.author.name, roles=[
        rol.name for rol in ctx.author.roles if rol.name != "@everyone"])

    receptor_t = EconomyUser(receptor.id, database_name, name=receptor.name, roles=[
        rol.name for rol in receptor.roles if rol.name != "@everyone"])

    status, transaction_id = core.transactions.new_transaction(
        sender, receptor_t, quantity, database_name, channel_name)
    if status == TransactionStatus.negative_quantity:
        await ctx.send(f"Cantidad invalida. No puedes enviar cantidades negativas o ningun {global_settings.coin_name}.")
    elif status == TransactionStatus.sender_not_exists:
        await ctx.send(f"Usuario no registrado. Registrate con {global_settings.prefix}registro.")
    elif status == TransactionStatus.receptor_not_exists:
        await ctx.send(f"{receptor.name} no es un usuario registrado.")
    elif status == TransactionStatus.sender_is_receptor:
        await ctx.send("Transferencia invalida. No puedes enviar {global_settings.coin_name} a ti mismo.")
    elif status == TransactionStatus.insufficient_coins:
        await ctx.send("Cantidad invalida. No tienes suficientes {global_settings.coin_name} para esta transacción.")
    elif status == TransactionStatus.succesful:
        await ctx.send("Transacción completada.")
        await ctx.author.send(f"Le transferiste al usuario {receptor.name}, ID: {receptor.id}, {quantity} "
                              f"{global_settings.coin_name}, tu saldo actual es de {sender.get_balance_from_db()['balance']} {global_settings.coin_name}.\n"
                              f"ID de transaccion: {transaction_id}")
        await receptor.send(f"El usuario {ctx.author.name}, ID: {ctx.author.id}, te ha transferido {quantity} "
                            f"{global_settings.coin_name}, tu saldo actual es de {receptor_t.get_balance_from_db()['balance']} {global_settings.coin_name}.\n"
                            f"ID de transacción: {transaction_id}")


@slash.slash(name=global_settings.coin_name, guild_ids=guild_ids, description=f"Escribe la cantidad de {global_settings.coin_name} del usuario")
async def get_coins(ctx: SlashContext):
    """Comando para solicitar un mensaje con la cantidad de monedas que el usuario tiene.

    Args:
        ctx (SlashContext): Context de discord
    """
    await ctx.defer()

    database_name = get_database_name(ctx.guild)
    user = EconomyUser(ctx.author.id, database_name)

    if user.user_exists():
        await ctx.send(f"Tu saldo actual es de {user.balance} {global_settings.coin_name} {ctx.author.name}.")
    else:
        await ctx.send(f"Usuario no registrado. Registrate con {global_settings.prefix}registro.")


@slash.slash(name="producto", guild_ids=guild_ids, description=f"Crea una oferta de un producto en un mensaje, manejando la compra de este a travéz de reacciones",
             options=[
              create_option(name="precio", description=f"precio en {global_settings.coin_name} del podcuto",
                            option_type=3, required=True),
              create_option(name="titulo", description=f"titulo del producto",
                            option_type=3, required=True),
              create_option(name="descripcion", description="descripcion del producto",
                            option_type=3, required=True),
              create_option(name="imagen", description=f"url de una imagen",
                            option_type=3, required=False)],
             connector={"precio": "price", "titulo": "title", "descripcion": "description", "imagen": "image"})
async def sell_product_in_shop(ctx: SlashContext, price, title, description, image="none"):
    """Comando para crear una interfaz de venta a un producto o servicio

    Args:
        ctx (SlashContext): Context de Discord
        price (float): Precio del producto
        title (str): Título del producto
        description (str): Descripción del producto
        image (str): Url de una imagen
    """
    await ctx.defer()

    try:
        price = round(float(price), global_settings.max_decimals)
    except:
        raise BadArgument

    database_name = get_database_name(ctx.guild)

    new_product = Product(ctx.author.id, title,
                          description, price, image, database_name)
    check = new_product.check_info()
    if check == ProductStatus.negative_quantity:
        await ctx.send("El precio de tu producto no puede ser cero ni negativo.", delete_after=2)
        return
    elif check == ProductStatus.seller_does_not_exist:
        await ctx.send(f"Usuario no registrado. Registrate con {global_settings.prefix}registro.`", delete_after=3)
        return

    embed = discord.Embed(title=f"${price} {title}", description=f"Vendedor: {ctx.author.name}\n{description}",
                          colour=discord.colour.Color.orange())
    if image != "none":
        new_product.image = image
        embed.set_image(url=image)

    msg = await ctx.send(embed=embed)
    new_product.id = msg.id
    new_product.send_to_db()

    await ctx.author.send(f"Tu producto ha sido registrado exitosamente. El ID de tu producto es: {new_product.id}")
    await msg.add_reaction("🪙")
    await msg.add_reaction("❌")


@slash.slash(name="editproducto", guild_ids=guild_ids, description=f"Transfiere {global_settings.coin_name} de tu wallet a un usuario",
             options=[
              create_option(name="id", description="identificador del producto",
                            option_type=3, required=True),
              create_option(name="precio", description="nuevo precio del producto",
                            option_type=3, required=False),
              create_option(name="titulo", description="nuevo titulo del producto",
                            option_type=3, required=False),
              create_option(name="descripcion", description="nueva descripcion del producto",
                            option_type=3, required=False),
              create_option(name="imagen", description=f"nueva url de una imagen (none para remover la imagen)",
                            option_type=3, required=False)],
             connector={"id": "_id", "precio": "price", "titulo": "title", "descripcion": "description", "imagen": "image"})
async def edit_product_in_shop(ctx: SlashContext, _id, price=0, title="0", description="0", image="0"):
    """Comando para editar una interfaz de venta a un producto o servicio, en los argumentos con valor por defecto no se
       haran cambios

    Args:
        ctx (SlashContext): Context de Discord
        _id (int): Id del producto
        price (float): Precio del producto, valor por defecto 0
        title (str): "Descripción del producto, valor por defecto _
        description (str): Título del producto, valor por defecto _
    """
    await ctx.defer()

    try:
        price = round(float(price), global_settings.max_decimals)
        _id = int(_id)
    except:
        raise BadArgument

    database_name = get_database_name(ctx.guild)
    status = core.store.edit_product(
        _id, ctx.author.id, database_name, price, title, description, image)

    if status == ProductStatus.seller_does_not_exist:
        await ctx.send(f"Usuario no registrado. Registrate con {global_settings.prefix}registro.", delete_after=2)
        return
    elif status == ProductStatus.no_exists_in_db:
        await ctx.send(f"ID invalido.", delete_after=2)
        return
    elif status == ProductStatus.user_is_not_seller_of_product:
        await ctx.send(f"No puedes modificar un producto que no es tuyo.", delete_after=3)
    elif status == ProductStatus.negative_quantity:
        await ctx.send("El precio no puede ser negativo.", delete_after=2)
        return

    product = query("_id", _id, database_name, CollectionNames.shop.value)

    embed = discord.Embed(title=f"${product['price']} {product['title']}", description=f"Vendedor: {ctx.author.name}\n{product['description']}",
                          colour=discord.colour.Color.orange())
    if product["image"] != "none":
        embed.set_image(url=product["image"])

    msg = await ctx.channel.fetch_message(_id)
    await msg.edit(embed=embed)

    await ctx.author.send(f"Tu producto ha sido editado exitosamente.")
    await ctx.send("Editado.", delete_after=2)


@slash.slash(name="delproducto", guild_ids=guild_ids, description="Elimina un producto",
             options=[
              create_option(name="id", description="identificador del producto (el id solo debe contener numeros)",
                            option_type=3, required=True)],
             connector={"id": "_id"})
async def del_product_in_shop(ctx: SlashContext, _id):
    """Comando para eliminar una interfaz de venta a un producto o servicio

    Args:
        ctx (SlashContext): Context de Discord
        _id (int): Id del producto en la base de datos
    """
    await ctx.defer()

    try:
        _id = int(_id)
    except:
        raise BadArgument

    database_name = get_database_name(ctx.guild)
    product, product_exists = Product.from_database(_id, database_name)

    if not product_exists:
        await ctx.send(f"ID invalido.", delete_after=2)
        return

    balance = query("_id", ctx.author.id, database_name,
                    CollectionNames.users.value)
    if balance is None:
        await ctx.send(f"Usuario no registrado. Registrate con {global_settings.prefix}registro.", 2)
        return

    if product.user_id == ctx.author.id:
        product.delete_on_db()
        try:
            msg = await ctx.channel.fetch_message(product.id)
            await msg.delete()
        except:
            pass
        await ctx.author.send(f"El producto {product.title} ha sido eliminado exitosamente.")
        await ctx.send("Eliminado.", delete_after=2)

    elif ctx.author.permissions_in(ctx.channel).administrator is True:
        product.delete_on_db()
        msg = await ctx.channel.fetch_message(product.id)
        await msg.delete()
        seller_user = await client.fetch_user(product.user_id)
        await seller_user.send(f"Tu producto {product.title} ha sido eliminado por el administrator "
                               f"{ctx.author.name}, ID {ctx.author .id}")

        await ctx.author.send(f"Has eliminado el producto {product.title}, del usuario {seller_user.name}, ID"
                              f" {seller_user.id}")
        await ctx.send("Eliminado.", delete_after=2)
    else:
        await ctx.send("No puedes eliminar este producto.", delete_after=2)


@slash.slash(name="productos", guild_ids=guild_ids, description="Busca tods los productos del usuario")
async def get_products_in_shop(ctx: SlashContext):
    """Comando para buscar todos los productos del usuario

    Args:
        ctx (SlashContext): Context de Discord
    """
    await ctx.defer()

    database_name = get_database_name(ctx.guild)
    balance = query("_id", ctx.author.id, database_name,
                    CollectionNames.users.value)
    if balance is None:
        await ctx.send(f"Usuario no registrado. Registrate con {global_settings.prefix}registro.")
        return

    products = core.store.get_user_products(ctx.author.id, database_name)
    embed = discord.Embed(colour=discord.colour.Color.gold(), title="Productos Encontrados",
                          description=f"Tabla de productos del usuario {ctx.author.name}")

    if len(products) == 0:
        embed.add_field(name="Nada", value="No tienes productos en venta.")

    for product in products:
        embed.add_field(
            name=f"{product.title}",
            value=f"ID:{product.id}, Precio: {product.price}")

    await ctx.send(embed=embed)


@slash.slash(name="usuarios", guild_ids=guild_ids, description="Entrega una lista de usuarios registrados a partir del nombre especificado",
             options=[
              create_option(name="nombre", description="nombre del usuario a busacar (@usuario o usuario)",
                            option_type=3, required=True)],
             connector={"nombre": "user"})
async def get_user_by_name(ctx: SlashContext, user):
    """Comando para buscar todos los usuarios que empiecen por _user

    Args:
        ctx (SlashContext): Context de Discord
        user (str): Nombre a buscar
    """

    database_name = get_database_name(ctx.guild)
    if user.startswith("@"):
        user = user[1:len(user)]

    users = core.users.get_users_starting_with(user, database_name)
    embed = discord.Embed(colour=discord.colour.Color.gold(), title="Usuarios Encontrados",
                          description=f"Tabla de todos los usuarios que inician con el nombre especificado.")

    if len(users) == 0:
        embed.add_field(name="Nada", value="Ningun usuario fue encontrado.")

    for user in users:
        embed.add_field(
            name=f"{user.name}",
            value=f"Nombre:{user.name}\nmonedas:{user.balance}")

    await ctx.send(embed=embed)


@slash.slash(name="validar", guild_ids=guild_ids, description="Valida una transaccion a partir de su ID",
             options=[
              create_option(name="id", description="Identificador de la transaccion",
                            option_type=3, required=True)],
             connector={"id": "_id"})
async def validate_transaction(ctx: SlashContext, _id):
    """Comando para validar una transaccion a travez de su id.

    Args:
        ctx (SlashContext): Context de Discord
        _id (float): Cantidad de monedas a imprimir
    """
    database_name = get_database_name(ctx.guild)
    transaction = query_id(
        _id, database_name, CollectionNames.transactions.value)

    if transaction is None:
        await ctx.send("ID invalido.")
    else:
        sender_user = await client.fetch_user(transaction["sender"]["_id"])
        receiver_user = await client.fetch_user(transaction["receiver"]["_id"])
        await ctx.channel.purge(limit=1)
        await ctx.author.send(f"Transacción {_id} válida")
        await ctx.author.send(embed=discord.Embed(title=f"${transaction['quantity']}",
                              description=f"Emisor: ID {sender_user.id}, Nombre: {sender_user.name}\n"
                                          f"Receptor: ID {receiver_user.id}, Nombre: {receiver_user.name}",
                              colour=discord.colour.Color.gold()))
        await ctx.send("Verificacion completa.")


@slash.slash(name="ayuda", guild_ids=guild_ids, description="Muestra la lista de comandos disponibles")
async def help_cmd(ctx: SlashContext):
    """Retorna la lista de comandos disponibles, Manda un mensaje con la información de los comandos del bot

    Args:
        ctx (SlashContext): Context de Discord
    """
    await ctx.defer()

    embed = discord.Embed(title=f"Ayuda | ECONOMY BOT {client.command_prefix}ayuda",
                          colour=discord.colour.Color.orange())

    embed.add_field(
        name=f"{client.command_prefix}registro",
        value="Registra una wallet con el nombre e id de tu usuario.",
        inline=False
    )

    embed.add_field(
        name=f"{client.command_prefix}desregistro",
        value="Elimina del registro al usuario y su wallet correspondiente.",
        inline=False
    )

    embed.add_field(
        name=f"{client.command_prefix}{global_settings.coin_name}",
        value=f"Entrega la cantidad de {global_settings.coin_name} que posee usuario.",
        inline=False
    )

    embed.add_field(
        name=f"{client.command_prefix}usuarios *nombre*",
        value="Entrega una lista de usuarios registrados a partir del nombre especificado\n\n"
              f"Ingresar:\n"
              "*nombre*: nombre del usuario a busacar (@usuario o usuario)",
        inline=False
    )

    embed.add_field(
        name=f"{client.command_prefix}transferir *cantidad* *receptor*",
        value=f"Transfiere {global_settings.coin_name} de tu wallet a un usuario\n\n"
              f"Ingresar:\n"
              f"*cantidad*: Cantidad de {global_settings.coin_name}.\n"
              f"*receptor*: Nombre del usuario receptor(@usuario o usuario).",
        inline=False
    )

    embed.add_field(
        name=f"{client.command_prefix}producto *precio* *titulo* *descripcion*",
        value=f"Crea una oferta de un producto en un mensaje, manejando la compra de este a travez de reacciones\n\n"
              f"Ingresar:\n"
              f"*precio*: Cantidad de {global_settings.coin_name}\n"
              f"*título*: Título del producto\n"
              f"*descripción*: Descripción del producto",
        inline=False
    )

    embed.add_field(
        name=f"{client.command_prefix}editproducto *id* *precio* *titulo* *descripcion*",
        value=f"Edita un producto, si se pone 0 en un argumento (excepto id) se dejara el valor previo\n\n"
              f"Ingresar:\n"
              f"*id*: ID del producto\n"
              f"*precio*: (Opcional) Nueva cantidad de {global_settings.coin_name}\n"
              f"*título*: (Opcional) Nuevo título del producto\n"
              f"*descripcion*: (Opcional) Nueva descripcion del producto",
        inline=False
    )

    embed.add_field(
        name=f"{client.command_prefix}delproducto *id*",
        value="Elimina un producto\n\n"
              "Ingresar:\n"
              "*id*: ID del producto",
        inline=False
    )

    embed.add_field(
        name=f"{client.command_prefix}productos",
        value="""Busca tods los productos del usuario.""",
        inline=False
    )

    embed.add_field(
        name=f"{client.command_prefix}validar *id*",
        value="Indica si una transacción es válida, a través de su ID\n\n"
              "Ingresar:\n"
              "*id*: Identificador de la transacción.",
        inline=False
    )

    embed.add_field(
        name=f"{client.command_prefix}bug *comando* *info*",
        value="Reporta un error a los desarrolladores. Por favor úsese con moderación.\n\n"
              "Ingresar:\n"
              "*comando*: Comando que ocasionó el error\n"
              "*info*: Descripcion o detalles del error",
        inline=False
    )

    await ctx.send(embed=embed)

"""Admin Commands"""


@client.command(name="imprimir")
@commands.has_permissions(administrator=True)
async def print_coins(ctx: SlashContext, quantity, receptor: discord.Member):
    """Comando que requiere permisos de administrador y sirve para agregar una cantidad de monedas a un usuario.

    Args:
        ctx (SlashContext): Context de Discord
        quantity (float): Cantidad de monedas a imprimir
        receptor (str): Mención al usuario receptor de las monedas
    """
    try:
        quantity = float(quantity)
    except:
        raise BadArgument

    if quantity <= 0:
        await ctx.send(f"No puedes imprimir cantidades negativas o cero {global_settings.coin_name}.")
        return
    quantity = round(quantity, global_settings.max_decimals)

    database_name = get_database_name(ctx.guild)
    receptor_b = EconomyUser(receptor.id, database_name)
    recipient_is_registered = receptor_b.user_exists()
    if not recipient_is_registered:
        await ctx.send(f"{receptor.name} no es un usuario registrado.")
        return

    receptor_b.balance += quantity

    await ctx.send(f"Se imprimieron {quantity} {global_settings.coin_name}, y se asignaron a {receptor_b.name}.\n"
                            f"ID {receptor_b._id}")


@client.command(name="expropiar")
@commands.has_permissions(administrator=True)
async def expropriate_coins(ctx: SlashContext, quantity, receptor: discord.Member):
    """Comando que requiere permisos de administrador y sirve para quitarle monedas a un usuario

    Args:
        ctx (SlashContext): Context de discord
        quantity (float): Cantidad que se le va a quitar a usuario
        receptor (str): Mención al usuario que se le van a quitar monedas
    """

    try:
        quantity = float(quantity)
    except:
        raise BadArgument

    if quantity <= 0:
        await ctx.send(f"no puedes expropiar cantidades negativas o ninguna moneda")
        return
    quantity = round(quantity, global_settings.max_decimals)

    database_name = get_database_name(ctx.guild)
    receptor_b = EconomyUser(receptor.id, database_name)
    recipient_is_registered = receptor_b.user_exists()
    if not recipient_is_registered:
        await ctx.send(f"{receptor.name} no es un usuario registrado")
        return

    receptor_b.balance -= quantity

    await ctx.send(f"se le expropiaron {quantity} monedas a {receptor_b.name}, id {receptor_b._id}")


#@slash.slash(name="stopforge", guild_ids=guild_ids, description="Detiene el forjado de monedas")
#@commands.has_permissions(administrator=True)
#async def stopforge(ctx: SlashContext):
#    """Detiene el forjado de monedas
#    Args:
#        ctx (SlashContext): Context de Discord
#    """
#
#    database_name = get_database_name(ctx.guild)
#    core.economy_management.stop_forge_coins(database_name)
#    await ctx.send("forjado de monedas detenido")
#
#
#@slash.slash(name="init", guild_ids=guild_ids, description="Inicia el forjado de monedas")
#@commands.has_permissions(administrator=True)
#async def init_economy(ctx: SlashContext):
#    """Con este comando se inizializa el forgado de monedas, cada nuevo forgado se le asigna una moneda a un usuario
#        random y se guarda un log del diccionario con los usuarios y su cantidad de monedas en la base de datos, estos
#        logs deben ser extraidos del host para poder realizar las estadisticas del experimento
#    Args:
#        ctx (SlashContext): Context de Discord
#    """
#
#    await ctx.channel.purge(limit=1)
#
#    database_name = get_database_name(ctx.guild)
#    users = query_all(database_name, CollectionNames.users.value)
#    if users.count() == 0:
#        await ctx.send('No hay usuarios registrados')
#        return
#
#    embed = discord.Embed(colour=discord.colour.Color.gold(), title="Tabla de Usuarios",
#                          description=f"Tabla de los usuarios registrados, con su nombre, id y cantidad de {global_settings.coin_name}.")
#
#    for user in users:
#        embed.add_field(
#            name=f"{user['name']}",
#            value=f"ID:{user['_id']}\n{global_settings.coin_name}:{user['balance']}")
#
#    # currency_tb = await ctx.channel.send(embed=embed)
#    await ctx.send(embed=embed)
#
#    while core.economy_management.forge_coins(database_name):
#        # TODO: futuro algoritmo de generacion de monedas
#        # Esperar para generar monedas, 900=15min
#        await asyncio.sleep(2)
#
#        random_user = db_utils.get_random_user(database_name)
#        random_user.balance += 1
#
#        # TODO: Log del forjado (DISCUSION)
#
#        # Pide toda la base de datos y puede ser muy pesado pedirla en cada forjado
#        # embed = discord.Embed(colour=discord.colour.Color.gold(), title="Tabla de Usuarios",
#        #                       description=f"tabla de todos los usuarios del bot, con su nombre, id y cantidad de monedas")
#        # users = query_all(database_name, CollectionNames.users.value)
#        # for user in users:
#        #     embed.add_field(
#        #         name=f"{user['name']}",
#        #         value=f"ID:{user['_id']}\nmonedas:{user['balance']}")
#
#        # await currency_tb.edit(embed=embed, content="")
#
#        await ctx.send(f"Nueva {global_settings.coin_name}, se le ha asignado a {random_user.name}")


@client.command(name="reset")
@commands.has_permissions(administrator=True)
async def reset_economy(ctx: SlashContext):
    """Pone los balances de todos los usuarios en 0, Requiere permisos de administrador

    Args:
        ctx (SlashContext): Context de Discord
    """
    db_name = get_database_name(ctx.guild)
    core.economy_management.reset_economy(db_name)

    await ctx.send(f"todos los usuarios tienen 0 {global_settings.coin_name}")


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
        name=f"{client.command_prefix}imprimir *cantidad* *usuario*",
        value=f"Imprime la cantidad especificada de {global_settings.coin_name} y las asigna a la wallet del usuario.\n\n"
              f"Ingresar:\n"
              f"*cantidad*: Cantidad de {global_settings.coin_name} a imprimir\n"
              "*usuario*: Mención del usuario (@user)",
        inline=False
    )

    embed.add_field(
        name=f"{client.command_prefix}expropiar",
        value=f"Elimina la cantidad especificada de {global_settings.coin_name} de la wallet del usuario.\n\n"
              f"Ingresar:\n"
              f"*cantidad*: Cantidad de {global_settings.coin_name} a expropiar\n"
              "*usuario*: Mención del usuario (@user)",
        inline=False
    )

    embed.add_field(
        name=f"{client.command_prefix}init",
        value=f"Inicializa el forgado de {global_settings.coin_name}.",
        inline=False
    )

    embed.add_field(
        name=f"{client.command_prefix}stopforge",
        value=f"Detiene el forjado de {global_settings.coin_name}.",
        inline=False
    )

    embed.add_field(
        name=f"{client.command_prefix}reset",
        value="Pone los balances de todos los usuarios en 0.",
        inline=False
    )

    await ctx.send(embed=embed)
