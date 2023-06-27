"""El modulo main llama inicializa la aplicacion llamando al cliente de discord y de la base de datos y demas modulos"""

from bot import discord_client
from database import mongo_client

from utils import utils

client = discord_client.get_client()

# los settings globales aplican a todos los servidores en que se encuentre el bot (prefix, token, )
global_settings = utils.get_global_settings()
mongo_client.init_database()

import bot.commands
import bot.events

client.run(global_settings.token)

mongo_client.close_client()
print("Disconnected")

""""
    Deployment
    
setup settings.json

python3 main.py
    
"""