"""Este modulo contiene los callback de eventos de discord"""

import bson
import discord
from discord.ext import commands

from bot.bot_utils import *
from bot.discord_client import get_client

from core.logger import report_bug_log
from core.transactions import new_transaction
from core.store import reaction_to_product

from models.economy_user import EconomyUser
from models.enums import TransactionStatus, TransactionType, CollectionNames
from models.product import Product

from database import db_utils
from utils.utils import get_global_settings, objectid_to_id, id_to_objectid

client = get_client()
global_settings = get_global_settings()


@client.event
async def on_ready():
    """Imprime información del cliente de discord cuando el bot ya está en línea
    """
    
    print("logged as")
    print(client.user.name)
    print(client.user.id)
    print('-----------')


@client.event
async def on_command_error(ctx, error):
    """Gestiona los errores que surgen en el procesamiento de los comandos

    Args:
        ctx (discord.ext.commands.Context): Context de discord
        error (discord.ext.commands.CommandError): TError lanzado en el comando
    """
    
    if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.CheckFailure):
        return

    msg = "ha ocurrido un error"
    if isinstance(error, commands.MissingRequiredArgument):
        msg = f"{msg}, faltan argumentos"
    elif isinstance(error, commands.BadArgument):
        msg = f"{msg}, un argumento no es valido"
    elif isinstance(error, commands.TooManyArguments):
        msg = f"{msg}, demasiados argumentos"
    elif isinstance(error, commands.MissingPermissions):
        msg = f"{msg}, no tienes permisos para realizar esta accion"
    elif isinstance(error, commands.BotMissingPermissions):
        msg = f"{msg}, de bot no tiene permisos para realizar esta accion"
    else:
        error = f"exception in {ctx.command.name}: {error}"
        print(error)
        if ctx.guild != None:
            report_bug_log(ctx.author.id, "Command Error", error, ctx.command.name, get_database_name(ctx.guild))
        msg = f"{msg}, ya ah sido reportado a los desarrolladores"

    await send_message(ctx, msg, auto_time=True)


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Evento de reaccion a un mensaje del bot, utilizado para el sistema de tienda

    Args:
        payload (discord.RawReactionActionEvent): Es el payload de la reacción
    """

    guild = client.get_guild(payload.guild_id)
    if guild is None:
        return
    
    database_name = get_database_name(guild)

    #Vericar que el usuario no sea un bot, y que el mensaje este registrado como producto
    product, product_exists = Product.from_database(id_to_objectid(payload.message_id), database_name)
    if payload.member.bot or not product_exists:
        return

    channel = discord.utils.get(guild.channels, id=payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    await msg.remove_reaction(payload.emoji, payload.member)

    remove_msg = await reaction_to_product(product, str(payload.emoji), payload.member, channel, database_name)
    if remove_msg:
        await msg.delete()
