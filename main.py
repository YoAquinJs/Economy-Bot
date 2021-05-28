import os

from db import bonobo_database
from client.client import get_client
client = get_client()

from commands.commands import *
from events.events import *

from utils.utils import get_global_settings

# region Settings
# los settings globales aplican a todos los servidores en que se encuentre el bot (prefix, token, )
global_settings = get_global_settings()

bonobo_database.init_database(global_settings['mongoUser'], global_settings['mongoPassword'])

# region ServerGlobal
# se aplica para todo el codigo y mas especifico cada server
current_dir = os.path.abspath(os.path.dirname("main.py"))
i = 0
for char in current_dir:
    if char == '\\':
        current_dir = f"{current_dir[0:i]}/{current_dir[i + 1:len(current_dir)]}"
    i += 1

if not(os.path.isdir(f"{current_dir}/local_settings")):
    os.mkdir("local_settings")

# endregion
client.run(global_settings["token"])

# anaconda commands
# cd documents\codeprojects\economy-bot\economy-bot
# conda activate bonoboenv
# python main.py
