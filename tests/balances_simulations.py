import discord


async def simulate_registration(dpytest, member: discord.Member) -> str:
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


async def simulate_desregistration(dpytest, member: discord.Member) -> str:
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


async def simulate_imprimir_monedas(dpytest, quantity: float, member: discord.Member, receiving_member: discord.Member) -> str:
    """Hace una simulacion del comando !imprimir

    Args:
        dpytest (module): referencia al modulo de dpytest
        member (discord.Member): Mienbro que va a imprimir las monedas (Tiene que tener permisos de administrador)
        receiving_member (discord.Member): Miembo al que se le van a dar las monedas impresas

    Returns:
        str: embed description
    """
    await dpytest.empty_queue()
    await dpytest.message(f'!imprimir {quantity} {receiving_member.mention}', member=member)

    return dpytest.get_embed().description


async def simulate_ver_monedas(dpytest, member: discord.Member) -> str:
    """Simula el comando !monedas para obtener el numero de monedas de member

    Args:
        dpytest (module): referencia al modulo de dpytest
        member (discord.Member): Mienbro que usara el comando !monedas

    Returns:
        str: embed description
    """
    await dpytest.empty_queue()
    await dpytest.message(f'!monedas {member.mention}', member=member)

    return dpytest.get_embed().description


async def simulate_expropiar(dpytest, quantity: float, member: discord.Member, admin: discord.Member) -> str:
    """Simula el comando !expropiar

    Args:
        dpytest (module): referencia al modulo de dpytest
        quantity (float): cantidad a expropiar
        admin (discord.Member): mienbro con permisos de administrador
        member (discord.Member): miembro al que se le va a expropiar

    Returns:
        str: embed description
    """
    await dpytest.empty_queue()
    await dpytest.message(f'!expropiar {quantity} {member.mention}', member=admin)

    return dpytest.get_embed().description


async def simulate_transferir(dpytest, member: discord.Member, quantity: float, receptor: discord.member) -> str:
    """Sumula el comando !transferir

    Args:
        dpytest (module): referencia al modulo de dpytest
        member (discord.Member): miembro que va a enviar monedas
        quantity (float): cantidad a enviar
        receptor (discord.member): mienbro que va a recibir monedas

    Returns:
        str: embed description
    """
    await dpytest.empty_queue()
    await dpytest.message(f'!transferir {quantity} {receptor.mention}', member=member)

    return dpytest.get_embed().description


async def simulate_usuarios(dpytest, buscar: str, member: discord.Member) -> discord.Embed:
    """Simula el comando !usuarios, busca a los usuarios que empiezan con el agumento buscar

    Args:
        dpytest (module): referencia al modulo de dpytest
        buscar (str): argumento para buscar
        member (discord.Member): miembro que va a ejecutar el comando

    Returns:
        discord.Embed: embed con los usuarios encontrados
    """
    await dpytest.empty_queue()
    await dpytest.message(f'!usuario {buscar}', member=member)

    return dpytest.get_embed()
