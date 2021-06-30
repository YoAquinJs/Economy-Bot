from bot.discord_client.discord_client import *
from bot.bot_utils import get_global_settings
from database.mongo_client import init_database, close_client

init_client()
client = get_client()

# los settings globales aplican a todos los servidores en que se encuentre el bot (prefix, token, )
global_settings = get_global_settings()
init_database()
print("data base initialized")

try:
    client.run(global_settings["token"])
except KeyboardInterrupt:
    client.logout()
    client.close()
finally:
    close_client()
    print("Disconnected")

# anaconda commands
# cd documents\codeprojects\economy-bot
# conda activate bonoboenv
# python main.py
