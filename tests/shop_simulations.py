from typing import Tuple
import discord


async def simulate_crearproducto(dpytest, member: discord.Member, price: float, title: str, desc: str) -> Tuple[discord.Embed, discord.Message]:
    """Simula el comando !producto para crear un producto

    Args:
        dpytest (module): modulo de dpytest
        member (discord.Member): Miembro que va a poner a la venta un producto
        price (float): precio del producto
        title (str): titulo del producto
        desc (str): descripcion del producto

    Returns:
        discord.Embed: embed del producto
    """
    await dpytest.empty_queue()
    await dpytest.message(f'!producto {price} {title}/{desc}', member=member)
    
    return (dpytest.get_embed(), dpytest.get_message())
