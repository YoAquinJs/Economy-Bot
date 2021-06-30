from bot import bot_utils, discord_client, commands, events
from core import economy_management, store, transactions, user
from database import mongo_client, db_utils

client = discord_client.get_client()

# los settings globales aplican a todos los servidores en que se encuentre el bot (prefix, token, )
global_settings = bot_utils.get_global_settings()
mongo_client.init_database()
print("data base initialized")

try:
    client.run(global_settings["token"])
except KeyboardInterrupt:
    client.logout()
    client.close()
finally:
    mongo_client.close_client()
    print("Disconnected")

# anaconda commands
# cd documents\codeprojects\economy-bot
# conda activate bonoboenv
# python main.py
