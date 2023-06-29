"""Este modulo contiene decoradores de comandosdel bot """

from discord.ext.commands import Context

from bot.bot_utils import send_message, get_database_name
from models.economy_user import EconomyUser
from utils.utils import get_global_settings, id_to_objectid

global_settings = get_global_settings()

def guild_required():
    def decorator(func):
        async def wrapper(ctx: Context, *args, **kwargs):
            
            if ctx.guild is not None:
                await func(ctx, *args, **kwargs)
            else:
                await send_message(ctx, "El comando debe ejecutarse en un servidor")    
        return wrapper
    
    return decorator

def register_required():
    def decorator(func):
        async def wrapper(ctx: Context, *args, **kwargs):
            
            if EconomyUser(id_to_objectid(ctx.author.id), get_database_name(ctx.guild)).get_data_from_db():
                await func(ctx, *args, **kwargs)
            else:
                await send_message(ctx, f"Usuario no registrado. Registrate con {global_settings.prefix}registro")    
        return wrapper
    
    return decorator