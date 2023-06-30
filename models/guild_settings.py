"""Este modulo contiene el modelo de GuildSettings"""

from database.db_utils import query
from utils.utils import id_to_objectid

from models.global_settings import GlobalSettings
from models.enums import CollectionNames


class GuildSettings():
    """Clase para manejar los settings de un servidor de discord

    Attributes:
        max_decimals (int): Numero de decimales maximos en los que se puede dividir la moneda
        economy_name (str): Nombre de la economia
        coin_name (str): Nombre de la moneda
        initial_number_of_coins (float): Numero de monedas que se le asigna a un usuario cuando se registra
    """
    
    max_decimals: int = ''
    economy_name: str = ''
    coin_name: str = ''
    initial_number_of_coins: float = 0.0

    def __init__(self, bson):
        """Crea objeto GuildSettings a partir de un bson
        """

        self.__dict__.update(bson)
        
    
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
            "initial_number_of_coins": global_settings.initial_number_of_coins
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
        del guild_settings['_id']
        
        return cls(guild_settings)