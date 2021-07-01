"""Contiene multiples metodos los cuales son utilizados por otros modulos, principalmente commands.py e events.py"""

import json
import pytz
import asyncio
import discord
import datetime

current_dir = None
_global_settings = None


def get_time():
    """Retorna el tiempo y hora actual en UTC

    Returns:
        srt: String Del Tiempo Actual
    """

    return str(datetime.datetime.now(pytz.utc))


def key_split(key, split_ch="_"):
    """Separa las llaves de los diccionarios tipo nombre_id (implementado para que en los logs y json se puedan identificar
       con usuario o nombre)
    """

    i = 0
    for ch in key:
        if ch == split_ch:
            break
        i = i + 1

    return [key[0:i], key[i+1:len(key)]]


async def send_message(ctx, text, title="", time=0, auto_time=False):
    """Envía un mensaje, convirtiendo el texto en un embed de discord

    Args:
        ctx (discord.ext.commands.Context): Context de discord
        text (str): Contenido del mensaje
        title (str, optional): titulo del mensaje
        time (int, optional): Especifica el tiempo a esperar para eliminar el mensaje, si es 0 es permanente,
        por defecto es 0
        auto_time (bool, optional): Especifica si despues de el tiempo de lectura promedio el mensaje sera eliminado,
        por defecto falso.
    """
    msg_txt = discord.Embed(title=title, description=text, colour=discord.colour.Color.gold())
    msg = await ctx.channel.send(embed=msg_txt)

    if auto_time is True:
        await ctx.channel.purge(limit=1)
        msg = await ctx.channel.send(embed=msg_txt)
        wpm = 180  # velocidad de lectura persona promedio
        time = (len(text) / len(text.split()))/wpm * 60 + 1
        await asyncio.sleep(time)
        await msg.delete()

    if time != 0:
        await asyncio.sleep(time)
        await msg.delete()

    return msg


def get_global_settings() -> dict:
    """Lee y parsea los settings.json a un diccionario de python

    Returns:
        dict: diccionario con los settings.json
    """

    global _global_settings

    if _global_settings is None:
        with open("settings.json", "r") as tmp:
            _global_settings = json.load(tmp)

    return _global_settings
