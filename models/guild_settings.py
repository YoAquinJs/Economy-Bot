"""Este modulo contiene el modelo de GuildSettings"""

import discord
from bot.discord_client import get_client
from database.db_utils import query, replace
from utils.utils import id_to_objectid, key_split

from models.global_settings import GlobalSettings
from models.enums import CollectionNames

client = get_client()


class GuildSettings():
    """Clase para manejar los settings de un servidor de discord

    Attributes:
        max_decimals (int): Numero de decimales maximos en los que se puede dividir la moneda
        economy_name (str): Nombre de la economia
        coin_name (str): Nombre de la moneda
        initial_number_of_coins (float): Numero de monedas que se le asigna a un usuario cuando se registra
        admin_role (discord.Role): Rol de administrador del bot en el servidor
        forge_time_span (int): Intervalo de segundos de cada forjado
        forge_quantity (float): Numero de monedas otorgadas por forjado
    """
    
    max_decimals: int = ''
    economy_name: str = ''
    coin_name: str = ''
    initial_number_of_coins: float = 0.0
    admin_role: discord.Role = None
    forge_time_span: int = 0
    forge_quantity: float = 0.0

    def __init__(self, bson):
        """Crea objeto GuildSettings a partir de un bson
        """

        self.__dict__.update(bson)
        
        
    def modify_in_db(self, database_name: str) -> bool:
        """Envia las modificaciones de la configuracion del bot a la base de datos

        Args:
            database_name (str): Nombre de la base de datos del servidor de discord

        Returns:
            bool: Si fue existoso o no
        """
        
        self.admin_role = 0 if self.admin_role is None else self.admin_role.id
        replace_result = replace('_id', id_to_objectid(0), self.__dict__, database_name, CollectionNames.settings.value)
        return replace_result.matched_count > 0
        
    
    @classmethod
    def from_global_settings(cls, global_settings: GlobalSettings):
        """Crea un GuildSettings a partir de un GlobalSettings, obteniendo los valores por defecto de servidores

        Args:
            global_settings (GlobalSettings): GlobalSettings para obtener los valores

        Returns:
            GuildSettings: Objeto GuildSettings con valores por defecto
        """
        
        return cls({
            "max_decimals": global_settings.max_decimals,
            "economy_name": global_settings.economy_name,
            "coin_name": global_settings.coin_name,
            "initial_number_of_coins": global_settings.initial_number_of_coins,
            "admin_role": None,
            "forge_time_span": global_settings.forge_time_span,
            "forge_quantity": global_settings.forge_quantity 
        })
        
    @classmethod
    def from_database(cls, database_name: str):
        """Crea un GuildSettings a partir de la configuracion guardada en la base de datos

        Args:
            database_name (str): Nombre de la base de datos del servidor de discord

        Returns:
            GuildSettings: Objeto GuildSettings con valores por defecto
        """
        
        guild_settings = query('_id', id_to_objectid(0), database_name, CollectionNames.settings.value)

        _, guild_id = key_split(database_name)
        guild = client.get_guild(int(guild_id))
        guild_settings["admin_role"] = None if guild_settings["admin_role"] == 0 else guild.get_role(guild_settings["admin_role"])
        
        return cls(guild_settings)