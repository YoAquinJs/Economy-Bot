import discord


async def simulate_registration(dpytest, member: discord.Member):
    """Simula el registro de un usuario y regresa la descripcion del embed

    Args:
        dpytest (module): referencia al modulo de dpytest
        member (discord.Member): usuario de discord que manda el mensaje

    Returns:
        str: Descripcion del modulo que responde al !registro
    """
    await dpytest.empty_queue()
    await dpytest.message('!registro', member=member)
    emb_desc = dpytest.get_embed().description

    return emb_desc


async def simulate_desregistration(dpytest, member: discord.Member):
    """Simula el desregistro de un usuario y regresa la descripcion del embed

    Args:
        dpytest (module): referencia al modulo de dpytest
        member (discord.Member): usuario de discord que manda el mensaje

    Returns:
        str: Descripcion del modulo que responde al !registro
    """
    await dpytest.empty_queue()
    await dpytest.message('!desregistro', member=member)
    emb_desc = dpytest.get_embed().description

    return emb_desc


async def simulate_imprimir_monedas(dpytest, quantity: float ,member: discord.Member, receiving_member: discord.Member):
    """Hace una simulacion del comando !imprimir

    Args:
        dpytest (module): referencia al modulo de dpytest
        member (discord.Member): Mienbro que va a imprimir las monedas (Tiene que tener permisos de administrador)
        receiving_member (discord.Member): Miembo al que se le van a dar las monedas impresas
    """
    await dpytest.empty_queue()
    await dpytest.message(f'!imprimir {quantity} {receiving_member.mention}', member=member)

    return dpytest.get_embed().description


async def simulate_ver_monedas(dpytest, member: discord.Member):
    """Simula el comando !monedas para obtener el numero de monedas de member

    Args:
        dpytest (module): referencia al modulo de dpytest
        member (discord.Member): Mienbro que usara el comando !monedas
    """
    await dpytest.empty_queue()
    await dpytest.message(f'!monedas {member.mention}', member=member)

    return dpytest.get_embed().description


async def simulate_expropiar(dpytest, quantity: float ,member: discord.Member):
    await dpytest.empty_queue()
    await dpytest.message(f'!expropiar {quantity} {member.mention}', member=member)

    return dpytest.get_embed().description
