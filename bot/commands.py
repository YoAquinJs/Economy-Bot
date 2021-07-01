"""Registra todos los comandos del bot"""

from discord.ext import commands
from discord.ext.commands import Context, BadArgument

from database.db_utils import *
from bot.discord_client import get_client
from bot.bot_utils import *

client = get_client()
global_settings = get_global_settings()


@client.command(name="stop")
async def stop_bot(ctx: Context):
    """Envia un mensaje con el ping del bot

    Args:
        ctx (Context): Context de discord
    """
    for dev_id in global_settings["dev_ids"]:
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

    balance = query("user_id", ctx.author.id, ctx.guild, Collection.balances.value)
    if balance is None:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings['prefix']}registro")
        return

    title_description = key_split(info, "/")

    bug = {
        "title": title_description[0],
        "description": title_description[1],
        "command": command
    }

    insert(bug, ctx.guild, Collection.bugs.value)

    for id in global_settings["dev_ids"]:
        dev = await client.fetch_user(id)
        await dev.send(f"BUG REPORT: {bug}")

    await send_message(ctx, "reportado")
    await ctx.author.send("gracias por reportar un bug, intentaremos solucionarlo lo antes posible.\n"
                          "porfavor no reenvie este bug o haga un mal uso del reporte, ya que obstruye el "
                          "trabajo de los desarrolladores")


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
        'balance': 0.0
    }

    insert(balance, ctx.guild, Collection.balances.value)

    await send_message(ctx, f"has sido añadido a la bonobo-economy {ctx.author.name}, tienes 0.0 monedas")


@client.command(name="desregistro")
async def de_register(ctx: Context, *, motive="nulo"):
    """ Comando para que un usuario se des registre, su balance se elimina de la base de datos de Mongo

    Args:
        ctx (Context): Context de discord
        motive (Str): Motivo del des registro, por defecto es nulo
    """

    balance = query("user_id", ctx.author.id, ctx.guild, Collection.balances.value)

    if balance is None:
        await send_message(ctx, f"{ctx.author.name} no estas registrado")
        return

    if exists("user_id", ctx.author.id, ctx.guild, Collection.shop.value) is True:
        await send_message(ctx, f"{ctx.author.name} tienes productos en la tienda registrados, primero eliminalos")
        return

    de_register_log = {
        "user_id": ctx.author.id,
        "user_name": ctx.author.name,
        "final_balance": balance["balance"],
        "motive": motive
    }

    insert(de_register_log, ctx.guild, Collection.deregisters.value)
    delete("user_id", balance["user_id"], ctx.guild, Collection.balances.value)

    await send_message(ctx, f"te has des registrado de la bonobo-economy {ctx.author.name}, lamentamos tu des registro")


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
        "sender_id": sender_balance['user_id'],
        "sender_roles": [rol.name for rol in ctx.author.roles if rol.name != "@everyone"],
        "receiver_id": receptor_balance['user_id'],
        "receiver_roles": [rol.name for rol in receptor.roles if rol.name != "@everyone"],
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

    balance = query("user_id", ctx.author.id, ctx.guild, Collection.balances.value)

    if balance is None:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings['prefix']}registro")
        return

    await send_message(ctx, f"tienes {balance['balance']} bonobo coins {ctx.author.name}")


@client.command(name="producto")
async def sell_product_in_shop(ctx: Context, price: float, *, info: str):
    """Comando para crear una interfaz de venta a un producto o servicio

    Args:
        ctx (Context): Context de Discord
        price (float): Precio del producto
        info (str): "Título"/"Descripción" del producto
    """

    balance = query("user_id", ctx.author.id, ctx.guild, Collection.balances.value)

    if balance is None:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings['prefix']}registro")
        return

    if len(info) == 0:
        await send_message(ctx, "tienes que ingresar un nombre")
        return

    name_description = key_split(info, "/")

    if price <= 0:
        await send_message(ctx, "el precio no puede ser negativo o 0")
        return

    await ctx.channel.purge(limit=1)

    msg = await send_message(ctx, f"Vendedor: {ctx.author.name}\n{name_description[1]}",
                             f"${price} {name_description[0]}")
    product = {
        "msg_id": msg.id,
        "price": price,
        "name": name_description[0],
        "description": name_description[1],
        "user_id": ctx.author.id
    }

    product = insert(product, ctx.guild, Collection.shop.value)

    await ctx.author.send(f"tu producto ah sido registrado exitosamente, este es el id del producto: "
                          f"{product.inserted_id}")
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

    balance = query("user_id", ctx.author.id, ctx.guild, Collection.balances.value)

    if balance is None:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings['prefix']}registro", 0, True)
        return

    product = query_id(_id, ctx.guild, Collection.shop.value)

    if product is None:
        await send_message(ctx, f"id invalido", 0, True)
        return

    try:
        price = float(price)
    except:
        raise BadArgument

    if price < 0:
        await send_message(ctx, "el precio no puede ser negativo", 0, True)
        return

    name_description = key_split(info, "/")

    if price != 0:
        modify("user_id", ctx.author.id, "price", price, ctx.guild, Collection.shop.value)
    else:
        price = product["price"]

    if name_description[0] != "0":
        modify("user_id", ctx.author.id, "name", name_description[0], ctx.guild, Collection.shop.value)
    else:
        name_description[0] = product["name"]

    if name_description[1] != "0":
        modify("user_id", ctx.author.id, "description", name_description[1], ctx.guild, Collection.shop.value)
    else:
        name_description[1] = product["description"]

    embed = discord.Embed(title=f"${price} {name_description[0]}", description=f"Vendedor: {ctx.author.name}\n"
                                                                               f"{name_description[1]}",
                          colour=discord.colour.Color.orange())

    msg = await ctx.channel.fetch_message(product["msg_id"])
    await msg.edit(embed=embed)

    await ctx.author.send(f"tu producto ah sido editado exitosamente")
    await send_message(ctx, "editado", 0, True)


@client.command(name="delproducto")
async def del_product_in_shop(ctx: Context, _id: str):
    """Comando para eliminar una interfaz de venta a un producto o servicio

    Args:
        ctx (Context): Context de Discord
        _id (str): Id del producto en la base de datos
    """

    balance = query("user_id", ctx.author.id, ctx.guild, Collection.balances.value)
    if balance is None:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings['prefix']}registro", 0, True)
        return

    product = query_id(_id, ctx.guild, Collection.shop.value)

    if product is None:
        await send_message(ctx, f"id invalido", 0, True)
        return

    if product["user_id"] == ctx.author.id:
        delete("msg_id", product["msg_id"], ctx.guild, Collection.shop.value)
        msg = await ctx.channel.fetch_message(product["msg_id"])
        await ctx.channel.purge(limit=1)
        await msg.delete()
        await ctx.author.send(f"has eliminado tu producto {product['name']}")

    elif ctx.author.permissions_in(ctx.channel).administrator is True:
        delete("msg_id", product["msg_id"], ctx.guild, Collection.shop.value)
        await ctx.channel.purge(limit=1)
        msg = await ctx.channel.fetch_message(product["msg_id"])
        await msg.delete()
        seller_user = await client.fetch_user(product["user_id"])
        await seller_user.send(f"tu producto {product['name']} ah sido eliminado por el administrator "
                               f"{ctx.author.name}, id {ctx.author .id}")

        await ctx.author.send(f"has eliminado el producto {product['name']}, del usuario {seller_user.name}, id"
                                  f" {seller_user.id}")
    else:
        await send_message(ctx, "no puedes eliminar este producto", 0, True)


@client.command(name="productos")
async def get_products_in_shop(ctx: Context):
    """Comando para buscar todos los productos del usuario

    Args:
        ctx (Context): Context de Discord
    """

    balance = query("user_id", ctx.author.id, ctx.guild, Collection.balances.value)
    if balance is None:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings['prefix']}registro")
        return

    products = query_all(ctx.guild, Collection.shop.value)

    embed = discord.Embed(colour=discord.colour.Color.gold(), title="Productos Encontrados",
                          description=f"tabla de productos del usuario {ctx.author.name}")

    product_found = False
    for product in products:
        if product["user_id"] == ctx.author.id:
            product_found = True
            embed.add_field(
                name=f"{product['name']}",
                value=f"ID:{product['_id']}, Precio: {product['price']}")

    if product_found is False:
        embed.add_field(name="Nada", value="ningun producto fue encontrado")

    await ctx.channel.send(embed=embed)


@client.command(name="usuario")
async def get_user_by_name(ctx: Context, *, _user: str):
    """Comando para buscar todos los usuarios que empiexen por _user

    Args:
        ctx (Context): Context de Discord
        _user (str): Nombre a buscar
    """

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
        embed.add_field(name="Nada", value="ningun usuario fue encontrado")

    await ctx.channel.send(embed=embed)


@client.command(name="validar")
async def validate_transaction(ctx: Context, _id: str):
    """Comando para validar una transaccion a travez de su id.

    Args:
        ctx (Context): Context de Discord
        _id (float): Cantidad de monedas a imprimir
    """

    transaction = query_id(_id, ctx.guild, Collection.transactions.value)

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
        value="Transfiere bonobo-coins de tu wallet a un usuario\n\n"
              "Argumentos: cantidad: cantidad de bonobo-coins; receptor: mencion del usuario receptor;",
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

    receptor_balance = query("user_id", receptor.id, ctx.guild, Collection.balances.value)

    if receptor_balance is None:
        await send_message(ctx, f"{receptor.name} no es un usuario registrado")
        return

    if quantity <= 0:
        await send_message(ctx, f"no puedes imprimir cantidades negativas o ninguna moneda")
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

    if quantity <= 0:
        await send_message(ctx, f"no puedes expropiar cantidades negativas o ninguna moneda")
        return

    if receptor_balance['balance'] < quantity:
        quantity = receptor_balance['balance']
        receptor_balance['balance'] = 0
    else:
        receptor_balance['balance'] -= quantity

    modify("user_id", receptor.id, "balance", receptor_balance['balance'], ctx.guild, Collection.balances.value)

    await send_message(ctx, f"se le expropiaron {quantity} monedas a {receptor_balance['user_name']}, "
                            f"id {receptor_balance['user_id']}")


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
    users = query_all(ctx.guild, Collection.balances.value)

    embed = discord.Embed(colour=discord.colour.Color.gold(), title="Tabla de Usuarios",
                          description=f"tabla de todos los usuarios del bot, con su nombre, id y cantidad de monedas")

    for user in users:
        embed.add_field(
            name=f"{user['user_name']}",
            value=f"ID:{user['user_id']}\nmonedas:{user['balance']}")

    currency_tb = await ctx.channel.send(embed=embed)

    while True:
        # futuro algoritmo de generacion de monedas
        await asyncio.sleep(10)  # Esperar para generar monedas, 900=15min

        random_user = query_rnd(ctx.guild, Collection.balances.value)
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

        insert(log_bson, ctx.guild, Collection.forge.value)

        embed = discord.Embed(colour=discord.colour.Color.gold(), title="Tabla de Usuarios",
                              description=f"tabla de todos los usuarios del bot, con su nombre, id y cantidad de monedas")
        users = query_all(ctx.guild, Collection.balances.value)
        for user in users:
            embed.add_field(
                name=f"{user['user_name']}",
                value=f"ID:{user['user_id']}\nmonedas:{user['balance']}")

        await currency_tb.edit(embed=embed, content="")

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
        modify("user_id", user['user_id'], "balance", 0, ctx.guild, Collection.balances.value)

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

    await ctx.send(embed=embed)
