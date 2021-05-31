import asyncio
import discord
import json
import os

current_dir = None
_global_settings = None


# separa las llaves de los diccionarios tipo nombre_id (implementado para que en los logs y json se pueda identificar
# usuario o nombre)
def key_split(key):
    i = 0
    for ch in key:
        if ch == "_":
            break
        i = i + 1

    return [key[0:i], key[i+1:len(key)]]


async def send_message(message, text, time):
    await asyncio.sleep(0.5)
    await message.channel.purge(limit=1)
    msg = discord.Embed(description=text, colour=discord.colour.Color.gold())
    d_msg = await message.channel.send(embed=msg)
    await asyncio.sleep(time)
    await message.channel.purge(limit=1)
    return d_msg


def init_server(guild):
    print(f"added {guild.name}, id: {guild.id}")
    new_settings = {
            "EconomicUsers": {},
            "Shop": {},
        }
    os.mkdir(f"local_settings/server_guild_{guild.id}")
    os.mkdir(f"local_settings/server_guild_{guild.id}/EconomyLogs")
    with open(f"local_settings/server_guild_{guild.id}/settings.json", "w") as guild_settings:
        json.dump(new_settings, guild_settings)


def settings(guild):
    with open(f"{server(guild)}/settings.json", "r") as file:
        return json.load(file)


def server(guild):
    path = f"{current_dir}/local_settings/server_guild_{guild.id}"
    if os.path.isdir(path) is False:
        init_server(guild)
    return path


def set_current_path():
    global current_dir

    current_dir = os.path.abspath(os.path.dirname("main.py"))
    i = 0
    for char in current_dir:
        if char == '\\':
            current_dir = f"{current_dir[0:i]}/{current_dir[i + 1:len(current_dir)]}"
        i += 1

    if not (os.path.isdir(f"{current_dir}/local_settings")):
        os.mkdir("local_settings")


def get_global_settings():
    global _global_settings
    
    if _global_settings is None:
        with open("settings.json", "r") as tmp:
            _global_settings = json.load(tmp)

    return _global_settings
