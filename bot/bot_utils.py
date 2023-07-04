"""Contiene multiples metodos los cuales son utilizados por otros modulos, principalmente commands.py e events.py"""

import asyncio
import discord
from discord.ext.commands import Context

current_dir = None

async def send_message(ctx: Context, text: str, title: str = '', time: int = 0, auto_time: bool = False, auto_delete_command: bool = False) -> discord.Message:
    """Envía un mensaje, convirtiendo el texto en un embed de discord

    Args:
        ctx (discord.ext.commands.Context): Context de discord
        text (str): Contenido del mensaje
        title (str, optional): titulo del mensaje. Defaults to ''.
        time (int, optional): Especifica el tiempo a esperar para eliminar el mensaje, si es 0 es permanente. Defaults to 0.
        auto_time (bool, optional): Especifica si despues de el tiempo de lectura promedio el mensaje sera eliminado. Defaults to False.
        auto_delete_command(bool, optional): Especifica si se elimina el mensaje que llamo al comando. Defaults to False.
        
    Returns:
        discord.Message: Mensaje enviado
    """
    
    msg_embed = discord.Embed(title=title, description=text, colour=discord.colour.Color.gold())
    msg = await ctx.channel.send(embed=msg_embed)

    if auto_delete_command is True:
        await ctx.message.delete()

    if auto_time is True:
        wpm = 200  # velocidad de lectura persona promedio
        time = (len(text) / len(text.split()))/wpm * 60 + 1
        await asyncio.sleep(time)
        await msg.delete()
    elif time != 0:
        await asyncio.sleep(time)
        await msg.delete()

    return msg


def get_database_name(guild: discord.Guild) -> str:
    """Esta función genera el nombre de la base de datos de una guild de discord

    Args:
        guild (discord.Guild): Información de un servidor de discord

    Returns:
        str: Nombre único de la base de datos para el server de discord
    """

    name = guild.name
    if len(name) > 20:
        # Esta comprobacion se hace porque mongo no acepta nombres de base de datos mayor a 64 caracteres
        name = name.replace("a", "")
        name = name.replace("e", "")
        name = name.replace("i", "")
        name = name.replace("o", "")
        name = name.replace("u", "")

        if len(name) > 20:
            name = name[:20]

    return f'{name.replace(" ", "_")}_{guild.id}'
