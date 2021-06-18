from events.events import *
from db import bonobo_database
from commands.commands import *
from client.client import get_client
from utils.utils import get_global_settings, set_current_path

client = get_client()
set_current_path()

# region Settings
# los settings globales aplican a todos los servidores en que se encuentre el bot (prefix, token, )
global_settings = get_global_settings()

# endregion
try:
    client.run(global_settings["token"])
except KeyboardInterrupt:
    client.logout()
    client.close()
finally:
    bonobo_database.close_client()
    print("Disconnected")

# anaconda commands
# cd documents\codeprojects\economy-bot
# conda activate bonoboenv
# python main.py
