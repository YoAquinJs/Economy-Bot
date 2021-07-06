from typing import List


class GlobalSettings():
    """Clase para manejar los global settings

    prefix (str): Prefijo del bot de discord
    token (str): Token del bot de discord
    mongoUser (str): usuario de mongo
    mongoPassword (str): Contraseña de mongo
    dev_ids (List(str)): id de discord de los desarroladores de bot 
    max_decimals (int): numero de decimales maximos en los que se puede dividir la moneda
    economy_name (str): Nombre de la economia
    coin_name (str):   Nombre de la moneda
    initial_number_of_coins (float): Numero de monedas que se le asigna a un usuario cuando se registra
    """
    prefix: str = ''
    token: str = ''
    mongoUser: str = ''
    mongoPassword: str = ''
    dev_ids: List[str] = []
    max_decimals: int = ''
    economy_name: str = ''
    coin_name: str = ''
    initial_number_of_coins: float = 0.0

    def __init__(self, **json):
        self.__dict__.update(json)