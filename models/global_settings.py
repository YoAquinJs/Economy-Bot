"""Este modulo contiene el modelo de GlobalSettings"""

class GlobalSettings():
    """Clase para manejar los global settings

    Attributes:
        token (str): Token del bot de discord
        mongoUser (str): usuario de mongo
        mongoPassword (str): Contraseña de mongo
        prefix (str): Prefijo de los comandos del bot de discord
        max_decimals (int): Numero de decimales maximos en los que se puede dividir la moneda por defecto en un servidor de discord
        economy_name (str): Nombre de la economia por defecto en un servidor de discord
        coin_name (str): Nombre de la moneda por defecto en un servidor de discord
        initial_number_of_coins (float): Numero de monedas que se le asigna a un usuario cuando se registra por defecto en un servidor de discord
        forge_time_span (int): Intervalo de segundos de cada forjado a por defecto en un servidor de discord
        forge_quantity (float): Numero de monedas otorgadas por forjado a por defecto en un servidor de discord
    """
    
    token: str = ''
    mongoUser: str = ''
    mongoPassword: str = ''
    prefix: str = ''
    max_decimals: int = ''
    economy_name: str = ''
    coin_name: str = ''
    initial_number_of_coins: float = 0.0
    forge_time_span: int = 0
    forge_quantity: float = 0.0
    
    def __init__(self, **json):
        """Crea objeto GlobalSettings a partir de un json
        """
        
        self.__dict__.update(json)