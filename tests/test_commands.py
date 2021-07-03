from tests.simulations import *
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
async def test_registro(bot):

    msg = await simulate_registration(dpytest, admin_member)
    desired_msg = f'has sido añadido a la bonobo-economy {admin_member.display_name}, tienes 0.0 monedas'

    db_utils.delete_database_guild(guild)
    assert desired_msg == msg


@pytest.mark.asyncio
async def test_desregistro(bot):

    msg = await simulate_registration(dpytest, admin_member)
    desired_msg = f'has sido añadido a la bonobo-economy {admin_member.display_name}, tienes 0.0 monedas'
    assert desired_msg == msg

    msg = await simulate_desregistration(dpytest, admin_member)
    desired_msg = f'te has des registrado de la bonobo-economy {admin_member.display_name}, lamentamos tu des registro'
    assert desired_msg == msg

    db_utils.delete_database_guild(guild)


@pytest.mark.asyncio
async def test_imprimir(bot):
    await simulate_registration(dpytest, admin_member)
    print_embed_desc = await simulate_imprimir_monedas(dpytest, 200, admin_member, admin_member)
    desired_print_embed_desc = f'se imprimieron 200.0, y se le asignaron a {admin_member.display_name}, id {admin_user.id}'

    assert print_embed_desc == desired_print_embed_desc

    monedas_embed_desc = await simulate_ver_monedas(dpytest, admin_member)
    desired_monedas_embed_desc = f'tienes 200.0 bonobo coins {admin_user.name}'

    assert monedas_embed_desc == desired_monedas_embed_desc
    db_utils.delete_database_guild(guild)


@pytest.mark.asyncio
async def test_expropiar(bot):
    await simulate_registration(dpytest, admin_member)
    print_embed_desc = await simulate_imprimir_monedas(dpytest, 200, admin_member, admin_member)
    desired_print_embed_desc = f'se imprimieron 200.0, y se le asignaron a {admin_member.display_name}, id {admin_user.id}'

    assert print_embed_desc == desired_print_embed_desc

    monedas_embed_desc = await simulate_ver_monedas(dpytest, admin_member)
    desired_monedas_embed_desc = f'tienes 200.0 bonobo coins {admin_user.name}'

    assert monedas_embed_desc == desired_monedas_embed_desc

    expropiar_embed_desc = await simulate_expropiar(dpytest, 10.75, admin_member, admin_member)
    desired_expropiar_embed_desc = f'se le expropiaron 10.75 monedas a {admin_user.name}, id {admin_user.id}'

    assert expropiar_embed_desc == desired_expropiar_embed_desc

    monedas_embed_desc = await simulate_ver_monedas(dpytest, admin_member)
    desired_monedas_embed_desc = f'tienes 189.25 bonobo coins {admin_user.name}'

    assert monedas_embed_desc == desired_monedas_embed_desc

    db_utils.delete_database_guild(guild)


@pytest.mark.asyncio
async def test_transferir(bot):
    await simulate_registration(dpytest, admin_member)
    print_embed_desc = await simulate_imprimir_monedas(dpytest, 200, admin_member, admin_member)
    desired_print_embed_desc = f'se imprimieron 200.0, y se le asignaron a {admin_member.display_name}, id {admin_user.id}'
    assert print_embed_desc == desired_print_embed_desc

    # Crea un nuevo usuario para simular una transferencia
    test_user = dpytest.backend.make_user(username='Test', discrim=2)
    test_member = dpytest.backend.make_member(test_user, guild)
    await simulate_registration(dpytest, test_member)

    trasferir_embed_desc = await simulate_transferir(dpytest, admin_member, 50.5, test_member)
    desired_trasferir_embed_desc = 'transaccion completa'

    assert trasferir_embed_desc == desired_trasferir_embed_desc

    # Ver si salen las cuentas en el admin
    balance_admin = await simulate_ver_monedas(dpytest, admin_member)
    desired_balance_admin = f'tienes 149.5 bonobo coins {admin_user.name}'

    assert balance_admin == desired_balance_admin

    # ver si salen las cuentas del usuario test
    balance_test = await simulate_ver_monedas(dpytest, test_member)
    desired_balance_test = f'tienes 50.5 bonobo coins {test_user.name}'

    assert balance_test == desired_balance_test
    db_utils.delete_database_guild(guild)
