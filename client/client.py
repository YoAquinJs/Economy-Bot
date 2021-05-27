import discord
from discord.ext import commands

client = None

def init_client(global_settings):
    global client
    
    intents = discord.Intents.default()
    intents.members = True

    client = commands.Bot(command_prefix=global_settings["prefix"], help_command=None,
                        activity=discord.Game(f"Migala Bot | {global_settings['prefix']}help"),
                        status=discord.Status.online, intents=intents)

