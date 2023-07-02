"""Este modulo contiene decoradores de comandosdel bot """

import discord

from utils.utils import id_to_objectid, get_global_settings
from bot.bot_utils import send_message, get_database_name

from models.economy_user import EconomyUser
from models.guild_settings import GuildSettings

_global_settings = get_global_settings()


def guild_required():
    """Verifica que comando se este ejecutando en un servidor de discord
    """
    
    async def predicate(ctx: discord.ext.commands.context) -> bool:
        if ctx.guild == None:
            await ctx.author.send("El comando debe ejecutarse en un servidor")
            
        return ctx.guild != None
    
    return discord.ext.commands.check(predicate)


def register_required():
    """Verifica que el usuario que intenta ejecutar el comando este registrado
    """
    
    async def predicate(ctx: discord.ext.commands.context) -> bool:
        database_name = get_database_name(ctx.guild)
        user_exists = EconomyUser(id_to_objectid(ctx.author.id),database_name ).get_data_from_db()
        if user_exists is False:
            await send_message(ctx, f"Usuario no registrado, Registrate con {_global_settings.prefix}registro", auto_time=True)

        return user_exists
    
    return discord.ext.commands.check(predicate)


def admin_required():
    """Verifica que el usuario que intenta ejecutar el comando sea un administrador del bot
    """
    
    async def predicate(ctx: discord.ext.commands.context) -> bool:
        database_name = get_database_name(ctx.guild)
        guild_settings = GuildSettings.from_database(database_name)

        have_admin = ctx.channel.permissions_for(ctx.author).administrator is True if guild_settings.admin_role is None else guild_settings.admin_role in ctx.author.roles

        if have_admin is False:
            await send_message(ctx, f"Usuario no posee permisos de administrador{'' if guild_settings.admin_role is None else f', debido a no poseer el rol {guild_settings.admin_role.mention}'}", auto_time=True)

        return have_admin
    
    return discord.ext.commands.check(predicate)
