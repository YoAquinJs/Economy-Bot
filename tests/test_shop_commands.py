import pytest
import discord.ext.test as dpytest
from discord import Permissions

from bot.commands import *
from bot.events import *
from bot.discord_client import get_client

from database import db_utils
from tests.balances_simulations import *
from tests.shop_simulations import *


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
    product_cost = 10.5
    product_title = 'title'
    product_description = 'desc'

    user1 = dpytest.backend.make_user(username='UsuarioTest', discrim=3)
    member1 = dpytest.backend.make_member(user1, guild)
    await simulate_registration(dpytest, member1)
    await simulate_imprimir_monedas(dpytest, 200, admin_member, member1)

    user2 = dpytest.backend.make_user(username='UsuarioTest 2', discrim=3)
    member2 = dpytest.backend.make_member(user2, guild)
    await simulate_registration(dpytest, member2)
    await simulate_imprimir_monedas(dpytest, 200, admin_member, member2)

    # Poner el producto en la tienda
    product_embed, product_message = await simulate_crearproducto(dpytest, member1, product_cost, product_title, product_description)
    desired_product_embed = discord.Embed(
        title=f"${product_cost} {product_title}", description=f"Vendedor: {member1.display_name}\n{product_description}", colour=discord.colour.Color.gold())

    assert dpytest.embed_eq(product_embed, desired_product_embed)
    db_utils.delete_database_guild(guild)
    # Da un error cuando se simulan las reacciones por eso este test esta incompleto


# @pytest.mark.asyncio
# async def test_editproducto(bot):
#     pass


# @pytest.mark.asyncio
# async def test_delproducto(bot):
#     pass


# @pytest.mark.asyncio
# async def test_buscarproductos(bot):
#     pass
