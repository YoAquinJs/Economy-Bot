import os
import json
import pytz
import asyncio
import discord
import datetime

current_dir = None
_global_settings = None


def get_time():
    return str(datetime.datetime.now(pytz.utc))


# separa las llaves de los diccionarios tipo nombre_id (implementado para que en los logs y json se pueda identificar
# usuario o nombre)
def key_split(key):
    i = 0
    for ch in key:
        if ch == "_":
            break
        i = i + 1

    return [key[0:i], key[i+1:len(key)]]


async def send_message(ctx, text, timer=False):
    msg_txt = discord.Embed(description=text, colour=discord.colour.Color.gold())
    if timer is False:
        await ctx.channel.send(embed=msg_txt)
    else:
        await ctx.channel.purge(limit=1)
        msg = await ctx.channel.send(embed=msg_txt)
        wpm = 180  # velocidad de lectura persona promedio
        time = (len(text) / len(text.split()))/wpm * 60 + 1
        await asyncio.sleep(time)
        await msg.delete()


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


def parse_mention_id(receptor_id):
    receptor_id = receptor_id.replace('<', "")
    receptor_id = receptor_id.replace('@', "")
    receptor_id = receptor_id.replace('!', "")
    receptor_id = int(receptor_id.replace('>', ""))

    return receptor_id