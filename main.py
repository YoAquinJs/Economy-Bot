import os
from db import bonobo_database
from client.client import get_client
from commands.commands import *
from events.events import *
from utils.utils import get_global_settings, set_current_path

client = get_client()
set_current_path()

# region Settings
# los settings globales aplican a todos los servidores en que se encuentre el bot (prefix, token, )
global_settings = get_global_settings()

bonobo_database.init_database(global_settings['mongoUser'], global_settings['mongoPassword'])

# region ServerGlobal
# se aplica para todo el codigo y mas especifico cada server

# endregion
client.run(global_settings["token"])

# anaconda commands
# cd documents\codeprojects\economy-bot\economy-bot
# conda activate bonoboenv
# python main.py
