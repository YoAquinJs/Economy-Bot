import pytest
import discord.ext.test as dpytest
from discord import Permissions

from bot.commands import *
from bot.events import *
from bot.discord_client import get_client

from database import db_utils


@pytest.fixture
def bot(event_loop):
    bot = get_client()
    bot.loop = event_loop

    dpytest.configure(bot)
    return bot


@pytest.mark.asyncio
async def test_registro(bot):
    guild = dpytest.get_config().guilds[0]

    await dpytest.message('!registro')

    emb_desc = dpytest.get_embed().description
    db_utils.delete_database_guild(guild)
    assert 'has sido añadido a la bonobo-economy' in emb_desc


@pytest.mark.asyncio
async def test_desregistro(bot):
    guild = dpytest.get_config().guilds[0]

    await dpytest.message('!registro')
    await dpytest.empty_queue()
    await dpytest.message('!desregistro')

    emb_desc = dpytest.get_embed().description
    db_utils.delete_database_guild(guild)

    assert 'te has des registrado de la bonobo-economy' in emb_desc


@pytest.mark.asyncio
async def test_imprimir(bot):
    guild = dpytest.get_config().guilds[0]
    admin_role = await guild.create_role(name="Admin", permissions=Permissions.all())

    test_user1 = dpytest.backend.make_user(username='Test', discrim=1)
    test_member1 = dpytest.backend.make_member(test_user1, guild)
    await test_member1.add_roles(admin_role)

    await dpytest.message('!registro', member=test_member1)

    await dpytest.empty_queue()
    await dpytest.message(f'!imprimir 200 {test_member1.mention}', member=test_member1)

    embed_desc_result = dpytest.get_embed().description
    desired_emb_desc = f'se imprimieron 200.0, y se le asignaron a {test_user1.name}, id {test_user1.id}'

    assert embed_desc_result == desired_emb_desc

    await dpytest.empty_queue()
    await dpytest.message(f'!monedas', member=test_member1)

    embed_desc_result = dpytest.get_embed().description
    desired_emb_desc = f'tienes 200.0 bonobo coins {test_user1.name}'

    db_utils.delete_database_guild(guild)
    assert embed_desc_result == desired_emb_desc
