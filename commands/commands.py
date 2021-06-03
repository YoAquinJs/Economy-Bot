from random import randint, random
from discord.ext import commands

from utils.utils import *
from db import bonobo_database
from client.client import get_client

client = get_client()

# region commands
@client.command(name="ping")
async def ping_chek(ctx):
    await send_message(ctx, f"latencia: {round(client.latency * 1000)}ms", 2)


# region Economics
# comando para que un usuario se registre, en este se añade un nuevo elemento al diccionario de usuarios y su cantidad
# de monedas correspondientes que inicia en 0
@client.command(name="regis")
async def register(ctx):
    # Se usaba para guardar los datos en un json
    # local_settings = settings(ctx.guild)
    # if f"{ctx.author.name}_{ctx.author.id}" in local_settings["EconomicUsers"].keys():
    #     await send_message(ctx, f"ya estas registrado, participa en la economia!", 3)
    #     return

    # local_settings["EconomicUsers"][f"{ctx.author.name}_{ctx.author.id}"] = {
    #     "coins": 0.0
    # }

    # json.dump(local_settings, open(f"{server(ctx.guild)}/settings.json", "w"))

    balance = bonobo_database.get_balance(ctx.author.id, ctx.guild)
    if balance is not None:
        await send_message(ctx, f"{ctx.author.name} ya estas registrado, tienes {balance['balance']} monedas", 3)
        return

    bonobo_database.create_balance(ctx.author.id, ctx.author.name, 0, ctx.guild)

    await send_message(ctx, f"has sido añadido a la bonobo-economy {ctx.author.name}, tienes 0.0 monedas", 3)


# comando para transferir monedas de la wallet del usuario a otro usuario
@client.command(name="transferir")
async def send_coins(ctx, quantity: float, receptor_id):
    receptor_id = parse_mention_id(receptor_id)
    
    if quantity <= 0:
        await send_message(ctx, f"no puedes enviar cantidades negativas o ninguna moneda", 3)
        return

    balance_of_sender = bonobo_database.get_balance(ctx.author.id, ctx.guild)
    balance_of_receptor = bonobo_database.get_balance(receptor_id, ctx.guild)

    if balance_of_sender is None:
        await send_message(ctx, f"{ctx.author.name} no estas registrado", 3)
        return

    if balance_of_receptor is None:
        await send_message(ctx, f"{receptor_id} no es un usuario registrado", 3)
        return

    if receptor_id == ctx.author.id:
        await send_message(ctx, "no te puedes auto transferir monedas", 3)
        return

    if balance_of_sender['balance'] < quantity:
        await send_message(ctx, "no tienes monedas suficientes", 3)
        return

    # Se hace la transaccion
    balance_of_sender['balance'] -= quantity
    balance_of_receptor['balance'] += quantity

    transacition_log = {
                "date": get_time(),
                "type": "transferencia",
                "sender": balance_of_sender['user_id'],
                "receptor": balance_of_receptor['user_id'],
                "quantity": quantity
            }
    bonobo_database.send_transaction(transacition_log, ctx.guild)

    bonobo_database.modify_balance(balance_of_receptor['user_id'], balance_of_receptor['balance'], ctx.guild)
    bonobo_database.modify_balance(balance_of_sender['user_id'], balance_of_sender['balance'], ctx.guild)

    await send_message(ctx, "transaccion completa", 2)
    await ctx.author.send(f"le transferiste a el usuario {balance_of_receptor['user_name']}, id {balance_of_receptor['user_id']}, {quantity} "
                          f"monedas, quedaste con {balance_of_sender['balance']} monedas")
    receptor = client.get_user(receptor_id)
    await receptor.send(f"el usuario {ctx.author.name}, id {ctx.author.id}, te ha transferido {quantity} "
                        f"monedas, has quedado con {balance_of_receptor['balance']} monedas")

    # local_settings = settings(ctx.guild)
    # economic_users = local_settings["EconomicUsers"]
    # receptor = await client.fetch_user(receptor_id)
    # receptor_key = f"{receptor.name}_{receptor_id}"
    # author_key = f"{ctx.author.name}_{ctx.author.id}"


    # if author_key in economic_users.keys():
    #     if economic_users[author_key]["coins"] >= quantity:
    #         economic_users[author_key]["coins"] -= quantity
    #         economic_users[receptor_key]["coins"] += quantity

    #         tran_bson = {
    #             "date": get_time(),
    #             "type": "transferencia",
    #             "sender": author_key,
    #             "receptor": receptor_key,
    #             "quantity": quantity
    #         }

    #         bonobo_database.send_transaction(tran_bson)

    #         local_settings["EconomicUsers"] = economic_users
    #         json.dump(local_settings, open(f"{server(ctx.guild)}/settings.json", "w"))
    #         await send_message(ctx, "transaccion completa", 2)
    #         await ctx.author.send(f"le transferiste a el usuario {receptor.name}, id {receptor.id}, {quantity} "
    #                               f"monedas, quedaste con {economic_users[author_key]['coins']} monedas")
    #         await receptor.send(f"el usuario {ctx.author.name}, id {ctx.author.id}, te ha transferido {quantity} "
    #                             f"monedas, has quedado con {economic_users[receptor_key]['coins']} monedas")
    #     else:
    #         await send_message(ctx, f"no tienes suficientos monedas", 3)
    # else:
    #     global_settings = get_global_settings()
    #     await send_message(ctx, f"no estas registrado, registrate con {global_settings['prefix']}regi", 3)


@client.command(name="monedas")
async def get_coins(ctx):
    # economic_users = settings(ctx.guild)["EconomicUsers"]
    # if not(f"{ctx.author.name}_{ctx.author.id}" in economic_users):
    #     global_settings = get_global_settings()
    #     await send_message(ctx, f"no estas registrado, registrate con {global_settings['prefix']}regi", 3)

    balance = bonobo_database.get_balance(ctx.author.id, ctx.guild)
    if balance is None:
        await send_message(ctx, f"{ctx.author.name} no estas registrado, utiliza el comando {client.get_prefix()}regis", 3)
        return

    await send_message(ctx, f"tienes {balance['balance']} bonobo coins "
                            f"{ctx.author.name}", 3)


@client.command(name="imprimir")
@commands.has_permissions(administrator=True)
async def print_coins(ctx, quantity: float, receptor_id: str):
    receptor_id = parse_mention_id(receptor_id)

    receptor = bonobo_database.get_balance(receptor_id, ctx.guild)
    receptor['balance'] += quantity
    bonobo_database.modify_balance(receptor['user_id'], receptor['balance'], ctx.guild)

    # receptor = await client.fetch_user(receptor_id)
    # local_settings = settings(ctx.guild)
    # local_settings["EconomicUsers"][f"{receptor.name}_{receptor.id}"]["coins"] += quantity
    # json.dump(local_settings, open(f"{server(ctx.guild)}/settings.json", "w"))
    await send_message(ctx, f"se imprimieron {quantity}, y se le asignaron a {receptor['user_name']}, id {receptor['user_id']}", 3)


@client.command(name="expropiar")
@commands.has_permissions(administrator=True)
async def expropriate_coins(ctx, quantity: float, receptor_id: str):
    receptor_id = parse_mention_id(receptor_id)

    receptor = bonobo_database.get_balance(receptor_id, ctx.guild)
    if receptor['balance'] < quantity:
        quantity = receptor['balance']
        receptor['balance'] = 0
    else:
        receptor['balance'] -= quantity

    bonobo_database.modify_balance(receptor['user_id'], receptor['balance'], ctx.guild)

    # receptor = await client.fetch_user(receptor_id)
    # local_settings = settings(ctx.guild)
    # local_settings["EconomicUsers"][f"{receptor.name}_{receptor.id}"]["coins"] -= quantity
    # json.dump(local_settings, open(f"{server(ctx.guild)}/settings.json", "w"))
    await send_message(ctx, f"se le expropiaron {quantity} monedas a {receptor['user_name']}, id {receptor['user_id']}", 3)


# con este comando se inizializa el forgado de monedas, cada nuevo forgado se le asigna una moneda a un usuario random
# y se guarda un log del diccionario con los usuarios y su cantidad de monedas, estos logs deben ser extraidos del host
# para poder realizar las estadisticas del experimento
@client.command(name="init")
@commands.has_permissions(administrator=True)
async def init_economy(ctx):
    await ctx.channel.purge(limit=1)
    currency_tb = await ctx.channel.send("_")
    # local_settings = settings(ctx.guild)
    # economic_users = local_settings['EconomicUsers']  # lee los setings.json del server
    users = bonobo_database.get_balances_cursor(ctx.guild)

    embed = discord.Embed(colour=discord.colour.Color.gold(), title="Tabla de Usuarios",
                          description=f"tabla de todos los usuarios del bot, con su nombre, id y cantidad de monedas")

    for user in users:
        embed.add_field(
            name=f"{user['user_name']}",
            value=f"ID:{user['user_id']}\nmonedas:{user['balance']}")

    
    await currency_tb.edit(embed=embed, content="")

    while True:
        await asyncio.sleep(10) # Esperar para generar monedas, 900=15min

        # local_settings = settings(ctx.guild)
        # economic_users = local_settings['EconomicUsers']  # lee los setings.json del server

        embed = discord.Embed(colour=discord.colour.Color.gold(), title="Tabla de Usuarios",
                              description=f"tabla de todos los usuarios del bot, con su nombre, id y cantidad de monedas")

        for user in users:
            embed.add_field(
            name=f"{user['user_name']}",
            value=f"ID:{user['user_id']}\nmonedas:{user['balance']}")

        # for key in economic_users.keys():
        #     key_values = key_split(key)
        #     embed.add_field(
        #         name=f"{key_values[0]}",
        #         value=f"ID:{key_values[1]}\nmonedas:{economic_users[key]['coins']}")
        await currency_tb.edit(embed=embed, content="")

        # Toma un usuario al azar para darle una moneda
        # rnd = randint(0, len(economic_users.keys()) - 1)
        # rnd_user = list(economic_users.keys())[rnd]
        random_user = bonobo_database.get_random_user(ctx.guild)
        random_user['balance'] += 1
        bonobo_database.modify_balance(random_user['user_id'], random_user['balance'], ctx.guild)
        # economic_users[rnd_user]["coins"] += 1

        # local_settings["EconomicUsers"] = economic_users
        # json.dump(local_settings, open(f"{server(ctx.guild)}/settings.json", "w"))

        log_bson = {
            "date": get_time(),
            "data": {
                'type': 'forjado',
                'user_id': random_user['user_id'],
                'user_name': random_user['user_name']
            } # Lo manda como object
        }
        bonobo_database.send_log(log_bson, ctx.guild)

        embed = discord.Embed(description=f"se le ha asignado a {random_user['user_name']}",
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
    # g = ctx.guild.members[0].guild

    # for m in g.members:
    #     print(m)

    # print(client.get_user(ctx.author.id))
    # print(client.get_user(609202751213404191))

    print('Probando bonobo database')

    res = bonobo_database.get_balance(ctx.author.id, ctx.guild)
    print(res)

    bonobo_database.modify_balance(ctx.author.id, 30, ctx.guild)
    res = bonobo_database.get_balance(ctx.author.id, ctx.guild)
    print(res)


@client.command(name="vender")
async def sell_in_shop(ctx, price: float, *, info: str):
    if len(info) == 0:
        await send_message(ctx, "tienes que ingresar un nombre", 3)
        return
    i = 0
    for ch in info:
        if ch == "/":
            name = info[0:i]
            description = info[i+1:len(info)]
            break
        i += 1

    if price <= 0:
        await send_message(ctx, "el precio no puede ser negativo o 0", 2)
        return

    local_settings = settings(ctx.guild)

    if not(f"{ctx.author.name}_{ctx.author.id}" in local_settings["EconomicUsers"].keys()):
        await send_message(ctx, f"no estas registrado, registrate con {client.command_prefix}regis", 3)
        return

    await ctx.channel.purge(limit=1)
    embed = discord.Embed(colour=discord.colour.Color.orange(), title=f"${price} {name}",
                          description=f"Vendedor:{ctx.author.name}\n{description}")
    msg = await ctx.channel.send(embed=embed)
    local_settings["Shop"][msg.id] = {
        "Price": price,
        "Name": name,
        "UserID": ctx.author.id
    }

    json.dump(local_settings, open(f"{server(ctx.guild)}/settings.json", "w"))
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
    # local_settings = settings(ctx.guild)
    # economic_users = local_settings["EconomicUsers"]

    users = bonobo_database.get_balances_cursor(ctx.guild)
    for user in users:
        bonobo_database.modify_balance(user['user_id'], 0, ctx.guild)

    # for key in economic_users.keys():
    #     economic_users[key]["coins"] = 0

    # local_settings["EconomicUsers"] = economic_users
    # json.dump(local_settings, open(f"{server(ctx.guild)}/settings.json", "w"))

    await send_message(ctx, "economia desde 0, todos los usuarios tienen 0 monedas", 3)
