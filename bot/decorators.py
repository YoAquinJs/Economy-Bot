"""Este modulo contiene decoradores de comandosdel bot """

import discord

from bot.bot_utils import send_message, get_database_name
from models.economy_user import EconomyUser
from utils.utils import get_global_settings, id_to_objectid

global_settings = get_global_settings()


def guild_required():
    """Verifica que comando se este ejecutando en un servidor de discord
    """
    
    async def predicate(ctx: discord.ext.commands.context):
        if ctx.guild == None:
            await ctx.author.send("El comando debe ejecutarse en un servidor")
            
        return ctx.guild != None
    
    return discord.ext.commands.check(predicate)

def register_required():
    """Verifica que el usuario que intenta ejecutar el comando este registrado
    """
    
    async def predicate(ctx: discord.ext.commands.context):
        user_exists = EconomyUser(id_to_objectid(ctx.author.id), get_database_name(ctx.guild)).get_data_from_db()
        if user_exists is False:
            await send_message(ctx, f"Usuario no registrado, Registrate con {global_settings.prefix}registro", auto_time=True)

        return user_exists
    
    return discord.ext.commands.check(predicate)
