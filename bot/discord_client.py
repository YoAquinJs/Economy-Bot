"""Maneja, distribuye y crea el cliente de discord.py, el cliente representa la conexión con la API de discord y su websocket en un objeto de Python."""

import discord
from discord.ext import commands
from utils.utils import get_global_settings

client = None


def init_client():
    """Inicializa el cliente de discord
    """

    global client
    global_settings = get_global_settings()

    intents = discord.Intents.default()
    intents.members = True

    client = commands.Bot(command_prefix=global_settings.prefix, help_command=None,
                          activity=discord.Game(f"Economy Bot | {global_settings.prefix}ayuda"),
                          status=discord.Status.online, intents=intents)


def get_client():
    """Es un singleton del cliente de discord, en caso de que el cliente no exista lo inicializa.

    Returns:
        discord.ext.commands.Bot: Cliente de discord
    """

    if client is None:
        init_client()

    return client
