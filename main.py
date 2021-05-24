import json
import pytz
import asyncio
import discord
import datetime
from random import randint
from moviepy.editor import *
from discord.ext import commands

# region Settings
with open("settings.json", "r") as tmp:
    global_settings = json.load(tmp)

client = commands.Bot(command_prefix=global_settings["prefix"], help_command=None,
                      activity=discord.Game(f"Migala Bot | {global_settings['prefix']}help"),
                      intents=discord.Intents.all(), status=discord.Status.online)

intents = discord.Intents(members=True)
welcome = discord.Client(intents=intents)

# endregion

# region Global
current_dir = os.path.abspath(os.path.dirname("main.py"))
i = 0
for char in current_dir:
    if char == '\\':
        current_dir = f"{current_dir[0:i]}/{current_dir[i + 1:len(current_dir)]}"
    i += 1


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
    os.rmdir(f"local_settings/server_guild_{guild.id}")


# endregion

# region commands
@client.command(name="ping")
async def ping_chek(ctx):
    await send_message(ctx, f"latencia: {round(client.latency * 1000)}ms", 2)


# region Economics
@client.command(name="regi")
async def register(ctx):
    local_settings = settings(ctx.guild)
    if ctx.author.name in local_settings["EconomicUsers"].keys():
        await send_message(ctx, f"ya estas registrado, participa en la economia!", 3)
        return

    local_settings["EconomicUsers"][ctx.author.name] = {
        "coins": 0.0
    }

    json.dump(local_settings, open(f"{server(ctx.guild)}/settings.json", "w"))
    await send_message(ctx, f"has sido añadido a la bonobo-economy {ctx.author.name},tus monedas son 0.0", 3)


@client.command(name="send")
async def send_coins(ctx, receptor, quantity: float):
    local_settings = settings(ctx.guild)
    economic_users = local_settings["EconomicUsers"]
    if not(receptor in economic_users.keys()):
        await send_message(ctx, f"{receptor} no es un usuario registrado", 3)
        return

    if ctx.author.name in economic_users.keys():
        if economic_users[ctx.author.name]["coins"] >= quantity:
            economic_users[ctx.author.name]["coins"] -= quantity
            economic_users[receptor]["coins"] += quantity
            await send_message(ctx,
                               f"transaccion completa, quedaste con {economic_users[ctx.author.name]['coins']} monedas"
                               , 3)
            local_settings["EconomicUsers"] = economic_users
            json.dump(local_settings, open(f"{server(ctx.guild)}/settings.json", "w"))
            await send_message(ctx, f"has sido añadido a la bonobo-economy {ctx.author.name},tus monedas son 0.0", 3)
        else:
            await send_message(ctx, f"no tienes suficientos monedas", 3)
    else:
        await send_message(ctx, f"no estas registrado, registrate con {global_settings['prefix']}regi", 3)


@client.command(name="init")
@commands.has_permissions(administrator=True)
async def init_economy(ctx):
    ctx.channel.purge(limit=1)
    i = 0
    for j in os.listdir(f"{server(ctx.guild)}/EconomyLogs"):
        logn = int(j[4])
        if logn >= i:
            i = i + i - logn + 1
    while True:
        local_settings = settings(ctx.guild)
        await asyncio.sleep(900)
        economic_users = local_settings['EconomicUsers']
        rnd = randint(0, len(economic_users.keys()) - 1)
        rnd_user = list(economic_users.keys())[rnd]
        economic_users[rnd_user]["coins"] += 1
        local_settings["EconomicUsers"] = economic_users
        json.dump(local_settings, open(f"{server(ctx.guild)}/settings.json", "w"))
        with open(f"{server(ctx.guild)}/EconomyLogs/log_{i}.txt", "w") as log:
            log.write(f"{str(datetime.datetime.now(pytz.utc))}\n{economic_users}")
        await ctx.channel.send(f"una nueva moneda se ah forjado, se le ah asignado a {rnd_user}")
        i += 1

# endregion

# Output the list of commands available
@client.command(name="help")
async def help_cmd(ctx):
    helpstr = discord.Embed(title=f"Ayuda | MIGALA BOT {client.command_prefix}help", colour=discord.colour.Color.orange())

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


# endregion
print("works")
client.run(global_settings["token"])
