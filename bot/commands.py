"""Este modulo registra todos los comandos del bot"""

import bson
from typing import Type
from discord.ext import commands
from discord.ext.commands import Context

from database import db_utils
from bot.discord_client import get_client
from bot.bot_utils import *
from bot.decorators import *

import core.economy_management
import core.logger
import core.transactions
import core.store
import core.users

from models.product import Product
from models.economy_user import EconomyUser
from models.enums import ProductStatus, TransactionStatus, TransactionType, CollectionNames, CommandNames
from utils.utils import get_global_settings, objectid_to_id, id_to_objectid, key_split

client = get_client()
global_settings = get_global_settings()


@client.command(name=CommandNames.ping.value)
async def ping_chek(ctx: Context):
    """Envia un mensaje con el ping del bot

    Args:
        ctx (discord.ext.commands.Context): Context de discord
    """

    await send_message(ctx, f"latencia: {round(client.latency * 1000)}ms", auto_time=True)


@client.command(name=CommandNames.bug.value)
@guild_required()
@register_required()
async def report_bug(ctx: Context, command: str, *, info: str):
    """Reporta un bug a los desarrolladores

    Args:
        ctx (discord.ext.commands.Context): Context de discord
        command (str): Comando que ocaciono el bug
        info (str): Titulo"/"descripcion del bug
    """
    
    database_name = get_database_name(ctx.guild)
    title_description = key_split(info, "/")

    work_successful, inserted_id = core.logger.report_bug_log(id_to_objectid(ctx.author.id), title_description[0], title_description[1], command, database_name)
    if work_successful:
        await send_message(ctx, "Reportado")
        await ctx.author.send(f"Gracias por reportar un bug, intentaremos solucionarlo lo antes posible.\n"
                              "Por favor no reenvíes este bug o haga un mal uso del reporte, recuerda"
                              "que los desarrolladores también somos personas.")
        await ctx.author.send(f'El ID de tu reporte "{title_description[0]}" es: {inserted_id}')
    else:
        await send_message(ctx, f"Usuario no registrado. Registrate con {global_settings.prefix}registro", auto_time=True)


@client.command(name=CommandNames.registro.value)
@guild_required()
async def register(ctx: Context):
    """Comando para que un usuario se registre, en este se añade un nuevo archivo a la base de datos de balances de
        usuarios y su cantidad de monedas correspondientes que inicia en 0

    Args:
        ctx (discord.ext.commands.Context): Context de discord
    """

    database_name = get_database_name(ctx.guild)
    new_user = EconomyUser(id_to_objectid(ctx.author.id), database_name, name=ctx.author.name)

    registereable, initial_balance = new_user.register()
    if registereable:
        core.economy_management.update_user_status(new_user._id, database_name)
        _, _ = core.transactions.new_transaction(None, new_user, initial_balance, database_name, TransactionType.initial_coins)
        await send_message(ctx, f'Has sido añadido a la {global_settings.economy_name} {new_user.name}, '
                                f'tienes {new_user.balance.balance} {global_settings.coin_name}')
    else:
        await send_message(ctx, f'{new_user.name} ya estas registrado', auto_time=True)


@client.command(name=CommandNames.desregistro.value)
@guild_required()
@register_required()
async def de_register(ctx: Context, *, motive: str = "nulo"):
    """Comando para que un usuario se desregistre, creando un UnregisterLog

    Args:
        ctx (discord.ext.commands.Context): Context de discord
        motive (str): Motivo del desregistro, por defecto es nulo
    """
    
    database_name = get_database_name(ctx.guild)
    user = EconomyUser(id_to_objectid(ctx.author.id), database_name)
    user_exists = user.get_data_from_db()
    
    if user_exists:
        products = core.store.get_user_products(id_to_objectid(ctx.author.id), database_name)

        if len(products) == 0:
            user.unregister()
            core.economy_management.update_user_status(user._id, database_name)
            core.logger.send_unregistered_log(user, motive)
            await send_message(ctx, f'{user.name} has salido de la {global_settings.economy_name}, lamentamos tu partida')
        else:
            await send_message(ctx, f'El usuario posee productos, primero elimina todos tus productos', auto_time=True)


@client.command(name=CommandNames.balance.value)
@guild_required()
@register_required()
async def get_coins(ctx: Context):
    """Comando para solicitar un mensaje con la cantidad de monedas que el usuario tiene.

    Args:
        ctx (discord.ext.commands.Context): Context de discord
    """
    
    database_name = get_database_name(ctx.guild)
    user = EconomyUser(id_to_objectid(ctx.author.id), database_name)
    exists = user.get_data_from_db()

    if exists:
        await ctx.message.delete()
        await ctx.author.send(f"Tu saldo actual es de {user.balance} {global_settings.coin_name} {ctx.author.name}.")
    else:
        await send_message(ctx, f"Usuario no registrado. Registrate con {global_settings.prefix}registro.", auto_time=True)


@client.command(name=CommandNames.usuario.value)
@guild_required()
async def get_user_by_name(ctx: Context, _user: discord.Member | str):
    """Comando para buscar todos los usuarios que empiecen por _user

    Args:
        ctx (discord.ext.commands.Context): Context de discord
        _user (discord.Member | str): Nombre o mencion de un usuario a buscar
    """

    users = []
    embed = discord.Embed(colour=discord.colour.Color.gold(), title="Usuarios Encontrados", description=f"Tabla de los usuarios con el nombre especificado")

    if isinstance(_user, str):
        users = core.users.get_users_starting_with(_user, get_database_name(ctx.guild))
        
        if len(users) == 0:
            embed.add_field(name="Ninguno", value="No se encontró ningún usuario.")
    else:
        fetched_user = EconomyUser(id_to_objectid(_user.id), get_database_name(ctx.guild))
        if fetched_user.get_data_from_db() is True:
            embed.add_field(
                name=f"{fetched_user.name}",
                value=f"ID: {objectid_to_id(fetched_user._id)}\n{global_settings.coin_name}: {fetched_user.balance}")

    for user in users:
        embed.add_field(
            name=f"{user.name}",
            value=f"ID: {objectid_to_id(user._id)}\n{global_settings.coin_name}: {user.balance}")

    await ctx.channel.send(embed=embed)


@client.command(name=CommandNames.transferir.value)
@guild_required()
@register_required()
async def transference(ctx: Context, quantity: float, receptor: discord.Member, *, reason: str = 'Nada'):
    """Comando para transferir monedas de la wallet del usuario a otro usuario

    Args:
        ctx (discord.ext.commands.Context): Context de discord
        quantity (float): Cantidad a transferir
        receptor (discord.Member): Mención a un usuario de discord
        reason (str): Razon de la transaccion
    """
    
    database_name = get_database_name(ctx.guild)

    sender = EconomyUser(id_to_objectid(ctx.author.id), database_name)
    receptor_euser = EconomyUser(id_to_objectid(receptor.id), database_name)

    status, transaction_id = core.transactions.new_transaction(sender, receptor_euser, quantity, database_name, TransactionType.user_to_user, reason=reason)
    
    if status == TransactionStatus.negative_quantity:
        await send_message(ctx, f"Cantidad invalida. No puedes enviar cantidades negativas o ningun {global_settings.coin_name}.", auto_time=True)
    elif status == TransactionStatus.sender_not_exists:
        await send_message(ctx, f"Usuario no registrado. Registrate con {global_settings.prefix}registro.", auto_time=True)
    elif status == TransactionStatus.receptor_not_exists:
        await send_message(ctx, f"{receptor.name} no es un usuario registrado.", auto_time=True)
    elif status == TransactionStatus.sender_is_receptor:
        await send_message(ctx, f"Transferencia invalida. No puedes enviar {global_settings.coin_name} a ti mismo.", auto_time=True)
    elif status == TransactionStatus.insufficient_coins:
        await send_message(ctx, f"No tienes suficientes {global_settings.coin_name} para esta transacción.", auto_time=True)
    elif status == TransactionStatus.succesful:
        await send_message(ctx, "Transacción completada.", auto_time=True)
        await ctx.author.send(f"Le transferiste al usuario {receptor.name}, ID: {receptor.id}, {quantity} "
                              f"{global_settings.coin_name}, tu saldo actual es de {sender.balance.value} {global_settings.coin_name}.\n"
                              f"ID de transaccion: {transaction_id}")

        await receptor.send(f"El usuario {ctx.author.name}, ID: {objectid_to_id(ctx.author.id)}, te ha transferido {quantity} "
                            f"{global_settings.coin_name}, tu saldo actual es de {receptor_euser.balance.value} {global_settings.coin_name}.\n"
                            f"ID de transacción: {transaction_id}")


@client.command(name=CommandNames.validar.value)
@guild_required()
@register_required()
async def validate_transaction(ctx: Context, _id: bson.ObjectId):
    """Comando para validar una transaccion a travez de su id.

    Args:
        ctx (discord.ext.commands.Context): Context de discord
        _id (bson.ObjectId): Id de transferencia a validar
    """
    
    transaction = db_utils.query("_id", _id, get_database_name(ctx.guild), CollectionNames.transactions.value)

    if transaction is None:
        await send_message(ctx, "ID invalido.", auto_time=True)
    else:
        await ctx.message.delete()
        await ctx.author.send(f"Transacción {_id} válida")
        
        system_user = EconomyUser.get_system_user()
        msg_embed = discord.Embed(title=f"${transaction['quantity']} ", description="", colour=discord.colour.Color.gold())
        msg_embed.set_footer(text=f"Timestamp: {transaction['date']}")
        
        if transaction["type"] == TransactionType.initial_coins.value:
            msg_embed.title += "de Balance inicial"
            receiver_user = await client.fetch_user(objectid_to_id(transaction["receiver_id"]))
            
            msg_embed.description = f"Emisor: Sistema\nReceptor: {receiver_user.name}, ID: {receiver_user.id}"   
        elif transaction["type"] == TransactionType.user_to_user.value:
            msg_embed.title += f"a razon de {transaction['reason']}"
            sender_user = await client.fetch_user(objectid_to_id(transaction["sender_id"]))
            receiver_user = await client.fetch_user(objectid_to_id(transaction["receiver_id"]))
            
            msg_embed.description = f"Emisor: {sender_user.name}, ID: {sender_user.id}\nReceptor: {receiver_user.name}, ID: {receiver_user.id}"
        elif transaction["type"] == TransactionType.shop_buy.value:
            msg_embed.title += f"{transaction['reason']}, ID del producto: {objectid_to_id(transaction['product_id'])}"
            sender_user = await client.fetch_user(objectid_to_id(transaction["sender_id"]))
            receiver_user = await client.fetch_user(objectid_to_id(transaction["receiver_id"]))

            msg_embed.description = f"Emisor: {sender_user.name}, ID: {sender_user.id}\nReceptor: {receiver_user.name}, ID: {receiver_user.id}"
        elif transaction["type"] == TransactionType.admin_to_user.value:
            msg_embed.title += f"por {transaction['reason']}"
            
            if transaction["sender_id"] == system_user._id:
                receiver_user = await client.fetch_user(objectid_to_id(transaction["receiver_id"]))
                msg_embed.description = f"Emisor: Sistema\nReceptor: {receiver_user.name}, ID: {receiver_user.id}"
            else:
                sender_user = await client.fetch_user(objectid_to_id(transaction["sender_id"]))
                msg_embed.description = f"Emisor: {sender_user.name}, ID: {sender_user.id}\nReceptor: Sistema"
        elif transaction["type"] == TransactionType.forged.value:
            msg_embed.title += "Forjados"
            receiver_user = await client.fetch_user(objectid_to_id(transaction["receiver_id"]))

            msg_embed.description = f"Emisor: Sistema\nReceptor: {receiver_user.name}, ID: {receiver_user.id}"   
        
        await ctx.author.send(embed=msg_embed)


@client.command(name=CommandNames.producto.value)
@guild_required()
@register_required()
async def sell_product_in_shop(ctx: Context, price: float, *, info: str):
    """Comando para crear una interfaz de venta a un producto o servicio

    Args:
        ctx (discord.ext.commands.Context): Context de discord
        price (float): Precio del producto
        info (str): "Título"/"Descripción" del producto
    """
    
    if len(info) == 0:
        await send_message(ctx, "Debes ingresar el nombre de la persona a la que deseas transferir.", auto_time=True)
        return

    name_description = key_split(info, "/")
    title = name_description[0]
    description = name_description[1]
    database_name = get_database_name(ctx.guild)

    new_product = Product(id_to_objectid(ctx.author.id), title, description, price, database_name)
    check = new_product.check_info()
    
    if check == ProductStatus.negative_quantity:
        await send_message(ctx, "El precio de tu producto no puede ser cero ni negativo.", auto_time=True)
        return
    elif check == ProductStatus.seller_does_not_exist:
        await send_message(ctx, f"Usuario no registrado. Registrate con {global_settings.prefix}registro.", auto_time=True)
        return

    await ctx.message.delete()

    msg_embed = discord.Embed(colour=discord.colour.Color.gold(), title=f"${price} {name_description[0]}",
                          description=f"Vendedor: {ctx.guild.get_member(ctx.author.id).mention}\n{name_description[1]}")
    msg = await ctx.channel.send(embed=msg_embed)
    new_product._id = id_to_objectid(msg.id)
    msg_embed.description += f"\n\nID: {msg.id}"
    await msg.edit(embed=msg_embed)
    
    new_product.send_to_db()

    await ctx.author.send(f"Tu producto ha sido registrado exitosamente. El ID de tu producto es: {msg.id}")
    await msg.add_reaction("🪙")
    await msg.add_reaction("❌")


@client.command(name=CommandNames.productos.value)
@guild_required()
@register_required()
async def get_products_in_shop(ctx: Context):
    """Comando para buscar todos los productos del usuario

    Args:
        ctx (discord.ext.commands.Context): Context de discord
    """
    
    database_name = get_database_name(ctx.guild)
    
    user = EconomyUser(id_to_objectid(ctx.author.id), database_name)
    user_exists = user.get_data_from_db()
    if user_exists is None:
        await send_message(ctx, f"Usuario no registrado. Registrate con {global_settings.prefix}registro.", auto_time=True)
        return

    products = core.store.get_user_products(user.id, database_name)
    embed = discord.Embed(colour=discord.colour.Color.gold(), title="Productos Encontrados",
                          description=f"Tabla de productos del usuario {ctx.author.name}")

    if len(products) == 0:
        embed.add_field(name="Nada", value="No tienes productos en venta.")

    for product in products:
        embed.add_field(name=f"{product.title}",
                        value=f"Precio: {product.price} {global_settings.coin_name}\nID: {objectid_to_id(product.id)}")

    await ctx.channel.send(embed=embed)


@client.command(name=CommandNames.delproducto.value)
@guild_required()
@register_required()
async def del_product_in_shop(ctx: Context, _id: int):
    """Comando para eliminar una interfaz de venta a un producto o servicio

    Args:
        ctx (discord.ext.commands.Context): Context de discord
        _id (int): Id del producto en la base de datos
    """

    database_name = get_database_name(ctx.guild)
    product, product_exists = Product.from_database(id_to_objectid(_id), database_name)

    if not product_exists:
        await send_message(ctx, f"ID invalido.", auto_time=True)
        return

    user_exists = EconomyUser(id_to_objectid(ctx.author.id), database_name).get_data_from_db()
    if user_exists is False:
        await send_message(ctx, f"Usuario no registrado. Registrate con {global_settings.prefix}registro.", auto_time=True)
        return

    channel = discord.utils.get(client.get_guild(ctx.guild.id).channels, id=ctx.channel.id)

    if objectid_to_id(product.user_id) == ctx.author.id:
        product.delete_on_db()
        msg = await ctx.channel.fetch_message(objectid_to_id(product.id))
        await msg.delete()
        await ctx.message.delete()
        await ctx.author.send(f"El producto {product.title} ha sido eliminado exitosamente.")
    elif channel.permissions_for(ctx.author).administrator: #Admin removal TODO to role checking
        product.delete_on_db()
        msg = await ctx.channel.fetch_message(objectid_to_id(product.id))
        await msg.delete()
        await ctx.message.delete()
        seller_user = await client.fetch_user(objectid_to_id(product.user_id))
        await seller_user.send(f"Tu producto {product.title} ha sido eliminado por el administrator "
                               f"{ctx.author.name}, ID {ctx.author .id}")

        await ctx.author.send(f"Has eliminado el producto {product.title}, del usuario {seller_user.name}, ID"
                              f" {seller_user.id}")
    else:
        await send_message(ctx, "No puedes eliminar este producto.", auto_time=True)


@client.command(name=CommandNames.ayuda.value)
async def help_cmd(ctx: Context):
    """Retorna la lista de comandos disponibles, Manda un mensaje con la información de los comandos del bot

    Args:
        ctx (discord.ext.commands.Context): Context de discord
    """
    
    embed = discord.Embed(title=f"ECONOMY BOT | {client.command_prefix}{CommandNames.ayuda.value}", colour=discord.colour.Color.orange(),
                          description="Lista de los comandos del Economy Bot")

    embed.add_field(
        name=f"{client.command_prefix}{CommandNames.registro.value}",
        value=f"Registra un usuario con su nombre, Id del serivor, y {global_settings.coin_name}'s iniciales",
    )

    embed.add_field(
        name=f"{client.command_prefix}{CommandNames.desregistro.value}",
        value="Elimina un usuario y se congela su wallet, al volverse a registrar se descongela con los fondos previos.",
    )

    embed.add_field(
        name=f"{client.command_prefix}{CommandNames.balance.value}",
        value=f"Muestra la cantidad de {global_settings.coin_name} que posee usuario.",
    )

    embed.add_field(
        name=f"{client.command_prefix}{CommandNames.usuario.value} *nombre*",
        value="Entrega los IDs de los usuarios encontrados a partir del nombre especificado\n\n"
              "Parametros:\n"
              "*nombre*: Usuario que se desea busacar (@usuario o usuario).",
    )

    embed.add_field(
        name=f"{client.command_prefix}{CommandNames.transferir.value} *cantidad* *receptor* *razon*",
        value=f"Transfiere {global_settings.coin_name} de tu wallet a la del usuario especificado\n\n"
              f"Parametros:\n"
              f"*cantidad*: Cantidad de {global_settings.coin_name}.\n"
              f"*receptor*: Nombre del usuario receptor (@usuario).\n"
              f"*razon*: Razon de la transaccion (opcional)",
    )

    embed.add_field(
        name=f"{client.command_prefix}{CommandNames.validar.value} *id*",
        value="Indica si una transacción es válida, a través de su ID\n\n"
              "Parametros:\n"
              "*id*: Identificador de la transacción.",
    )

    embed.add_field(
        name=f"{client.command_prefix}{CommandNames.producto.value} *precio* *info*",
        value="Crea un producto en un mensaje. La compra se realizará a través de reacciones.\n\n"
              "Parametros:\n"
              f"*precio*: Cantidad de {global_settings.coin_name}\n"
              "*info*: Nombre/description, separar el nombre y la descripcion con '/'",
    )

    #embed.add_field(
    #    name=f"{client.command_prefix}editproducto *id* *precio* *info*",
    #    value="""Edita un producto. Si se pone 0 en *precio* o *info*, se dejará el valor previo.\n\n"
    #          "Parametros:\n"
    #          "*id*: ID del producto\n"
    #          "*precio*: Cantidad de monedas\n"
    #          "*info*: Nombre"/"description""",
    #)

    embed.add_field(
        name=f"{client.command_prefix}{CommandNames.bug.value} *comando* *info*",
        value="Reporta un error a los desarrolladores. Por favor úsese con moderación.\n\n"
              "Parametros:\n"
              "*comando*: Comando que ocasionó el error\n"
              "*info*: Título/descripción del error, separar titulo y descripcion con '/'"
    )
    
    embed.add_field(
        name=f"{client.command_prefix}{CommandNames.delproducto.value} *id*",
        value="""Elimina un producto del propio usuario, o por accion de un administrador\n\n"
              "Parametros:\n"
              "*id*: ID del producto""",
    )

    embed.add_field(
        name=f"{client.command_prefix}{CommandNames.productos.value}",
        value="""Busca todos los productos del usuario.""",
    )
    
    #Formatting
    embed.add_field(name="",value="")

    await ctx.send(embed=embed)


@client.command(name=CommandNames.imprimir.value)
@commands.has_permissions(administrator=True)
@guild_required()
@register_required()
async def print_coins(ctx: Context, quantity: float, receptor: discord.Member):
    """Comando que requiere permisos de administrador y sirve para agregar una cantidad de monedas a un usuario.

    Args:
        ctx (discord.ext.commands.Context): Context de discord
        quantity (float): Cantidad de monedas a imprimir
        receptor (str): Mención al usuario receptor de las monedas
    """
    
    database_name = get_database_name(ctx.guild)

    admin_euser = EconomyUser(id_to_objectid(ctx.author.id), database_name)
    receptor_euser = EconomyUser(id_to_objectid(receptor.id), database_name)

    status, transaction_id = core.transactions.new_transaction(None, receptor_euser, quantity, database_name, TransactionType.admin_to_user, admin=admin_euser)
    
    if status == TransactionStatus.sender_not_exists:
        await send_message(ctx, f"Usuario no registrado. Registrate con {global_settings.prefix}registro.", auto_time=True)
    if status == TransactionStatus.negative_quantity:
        await send_message(ctx, f"Cantidad invalida. No puedes imprimir cantidades negativas o cero {global_settings.coin_name}.", auto_time=True)
    elif status == TransactionStatus.receptor_not_exists:
        await send_message(ctx, f"{receptor.name} no es un usuario registrado.", auto_time=True)
    elif status == TransactionStatus.succesful:
        await send_message(ctx, f"Se imprimieron {quantity} {global_settings.coin_name}, y se asignaron al usuario {receptor.name}, ID: {receptor.id}\n"
                              f"ID de transaccion: {transaction_id}")
        await receptor.send(f"El administrador {ctx.author.name}, ID: {ctx.author.id}, te ha impreso {quantity} {global_settings.coin_name},"
                            f"tu saldo actual es de {receptor_euser.balance.value} {global_settings.coin_name}.\n"
                            f"ID de transacción: {transaction_id}")


@client.command(name=CommandNames.expropiar.value)
@commands.has_permissions(administrator=True)
@guild_required()
@register_required()
async def expropriate_coins(ctx: Context, quantity: float, receptor: discord.Member):
    """Comando que requiere permisos de administrador y sirve para quitarle monedas a un usuario

    Args:
        ctx (Context): Context de discord
        quantity (float): Cantidad que se le va a quitar a usuario
        receptor (str): Mención al usuario que se le van a quitar monedas
    """

    database_name = get_database_name(ctx.guild)

    admin_euser = EconomyUser(id_to_objectid(ctx.author.id), database_name)
    receptor_euser = EconomyUser(id_to_objectid(receptor.id), database_name)

    status, transaction_id = core.transactions.new_transaction(receptor_euser, None, quantity, database_name, TransactionType.admin_to_user, admin=admin_euser)
    
    if status == TransactionStatus.sender_not_exists:
        await send_message(ctx, f"Usuario no registrado. Registrate con {global_settings.prefix}registro.", auto_time=True)
    if status == TransactionStatus.negative_quantity:
        await send_message(ctx, f"Cantidad invalida. No puedes imprimir cantidades negativas o cero {global_settings.coin_name}.", auto_time=True)
    elif status == TransactionStatus.receptor_not_exists:
        await send_message(ctx, f"{receptor.name} no es un usuario registrado.", auto_time=True)
    elif status == TransactionStatus.succesful:
        await send_message(ctx, f"Se expropiaron {quantity} {global_settings.coin_name} al usuario {receptor.name}, ID: {receptor.id}\n"
                           f"ID de transaccion: {transaction_id}")
        await receptor.send(f"El administrador {ctx.author.name}, ID: {ctx.author.id}, te ha expropiado {quantity} {global_settings.coin_name},"
                            f"tu saldo actual es de {receptor_euser.balance.value} {global_settings.coin_name}.\n"
                            f"ID de transacción: {transaction_id}")


@client.command(name=CommandNames.initforge.value)
@commands.has_permissions(administrator=True)
@guild_required()
@register_required()
async def init_forge(ctx: Context):
    """Con este comando se inizializa el forgado de monedas, cada nuevo forgado se le asigna una moneda a un usuario
        random y se guarda un log del diccionario con los usuarios y su cantidad de monedas en la base de datos
        
    Args:
        ctx (discord.ext.commands.Context): Context de discord
    """


    database_name = get_database_name(ctx.guild)
        
    await ctx.message.delete()
    embed = discord.Embed(colour=discord.colour.Color.gold(), title="Forjado de Monedas",
                          description=f"Cada {15} segundos se forjaran {1} {global_settings.coin_name}.")
    await ctx.channel.send(embed=embed)

    fetched_users = db_utils.query_all(database_name, CollectionNames.users.value).find({})
    core.economy_management._users[database_name] = [user["_id"] for user in fetched_users]

    core.economy_management.forge_coins_status(database_name, True)

    wait_time = 15
    while core.economy_management.is_forging(database_name):
        # Esperar para generar monedas  
        wait_time = 15

        random_user = core.users.get_random_user(core.economy_management._users[database_name], database_name)
        if random_user._id == EconomyUser.get_system_user()._id:
            asyncio.create_task(send_message(ctx, "Ningun usuario registrado, moneda asignada al sistema", time=15))
            continue
        else:
            status, transaction_id = core.transactions.new_transaction(None, random_user, 1, database_name, TransactionType.forged)

            if status == TransactionStatus.receptor_not_exists:
                fetched_users = db_utils.query_all(database_name, CollectionNames.users.value).find({})
                core.economy_management._users[database_name] = [user["_id"] for user in fetched_users]
                wait_time = 0
            else:
                asyncio.create_task(send_message(ctx, f"Se ha asignado a {random_user.name}", f"Se han forjado {1} {global_settings.coin_name}", time=15))
                asyncio.create_task(ctx.guild.get_member(objectid_to_id(random_user._id)).send(f"Se te han asignado {1} {global_settings.coin_name} forjadas,\n "
                                                                 f"tu saldo actual es de {random_user.balance.value} {global_settings.coin_name}.\n"
                                                                 f"ID de transacción: {transaction_id}"))
        await asyncio.sleep(wait_time)


@client.command(name=CommandNames.stopforge.value)
@commands.has_permissions(administrator=True)
@guild_required()
@register_required()
async def stop_forge(ctx: Context):
    """Detiene el forjado de monedas en el servidor

    Args:
        ctx (discord.ext.commands.Context): Context de discord
    """
    
    database_name = get_database_name(ctx.guild)
    core.economy_management.forge_coins_status(database_name, False)
    
    await send_message(ctx, "Se ha detenido el forjado", auto_time=True)


@client.command(name=CommandNames.reset.value)
@commands.has_permissions(administrator=True)
@guild_required()
@register_required()
async def reset_economy(ctx: Context):
    """Reinicia los balances de todos los usuarios a la configuracion de initial_coins, Requiere permisos de administrador

    Args:
        ctx (discord.ext.commands.Context): Context de discord
    """
    
    core.economy_management.reset_economy(get_database_name(ctx.guild))

    await send_message(ctx, f"Todos los usuarios tienen {global_settings.initial_number_of_coins} {global_settings.coin_name}.")


@client.command(name=CommandNames.adminayuda.value)
async def admin_help_cmd(ctx: Context):
    """Retorna la lista de comandos disponibles para los admins, Manda un mensaje con la información de los comandos del
       bot

    Args:
        ctx (discord.ext.commands.Context): Context de discord
    """

    embed = discord.Embed(title=f"Ayuda | ECONOMY BOT {client.command_prefix}help",
                          colour=discord.colour.Color.orange())

    embed.add_field(
        name=f"{client.command_prefix}imprimir *cantidad* *usuario*",
        value=f"Imprime la cantidad especificada de {global_settings.coin_name} y las asigna a la wallet del usuario.\n\n"
              "Argumentos:\n"
              f"*cantidad*: Cantidad de {global_settings.coin_name} a imprimir\n"
              "*usuario*: Mención (@user)",
    )

    embed.add_field(
        name=f"{client.command_prefix}expropiar *cantidad* *usuario*",
        value=f"Elimina la cantidad especificada de {global_settings.coin_name} de la wallet del usuario.\n\n"
              "Argumentos:\n"
              f"*cantidad*: Cantidad de {global_settings.coin_name} a expropiar\n"
              "*usuario*: Mención (@user)",
    )

    embed.add_field(
        name=f"{client.command_prefix}reset",
        value="Pone los balances de todos los usuarios en 0."
    )
    
    embed.add_field(
        name=f"{client.command_prefix}initforge",
        value=f"Inicializa el forgado de {global_settings.coin_name}."
    )

    embed.add_field(
        name=f"{client.command_prefix}stopforge",
        value=f"Detiene el forjado de {global_settings.coin_name}."
    )

    embed.add_field(name="", value="")
    
    await ctx.send(embed=embed)
