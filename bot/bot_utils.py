"""Contiene multiples metodos los cuales son utilizados por otros modulos, principalmente commands.py e events.py"""

import asyncio
import discord

current_dir = None

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
    msg_txt = discord.Embed(title=title, description=text,
                            colour=discord.colour.Color.gold())
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


def get_database_name(guild: discord.Guild) -> str:
    """Esta función genera el nombre de la base de datos de una guild de discord

        Args:
                guild (discord.Guild): Es la información de una Guild de discord

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
