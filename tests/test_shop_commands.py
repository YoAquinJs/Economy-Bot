from tests.balances_simulations import *
import pytest
import discord.ext.test as dpytest
from discord import Permissions

from bot.commands import *
from bot.events import *
from bot.discord_client import get_client

from database import db_utils


admin_user = None
admin_member = None
guild = None


@pytest.fixture
async def bot(event_loop):
    global admin_user, admin_member, guild

    bot = get_client()
    bot.loop = event_loop

    dpytest.configure(bot)
    guild = dpytest.get_config().guilds[0]
    db_utils.delete_database_guild(guild)

    admin_user = dpytest.backend.make_user(username='Admin', discrim=1)
    admin_member = dpytest.backend.make_member(admin_user, guild)
    admin_role = await guild.create_role(name="Admin", permissions=Permissions.all())
    await admin_member.add_roles(admin_role)

    return bot


@pytest.mark.asyncio
async def test_producto(bot):
    pass


@pytest.mark.asyncio
async def test_editproducto(bot):
    pass


@pytest.mark.asyncio
async def test_delproducto(bot):
    pass


@pytest.mark.asyncio
async def test_buscarproductos(bot):
    pass
