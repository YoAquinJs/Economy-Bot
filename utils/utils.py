"""El módulo utils provee metodos generales usadas en demas modulos"""

import bson
import json
import datetime
from datetime import datetime
from typing import Union

from models.global_settings import GlobalSettings

global _global_settings
_global_settings = None


def get_global_settings() -> GlobalSettings:
    """Lee y parsea los settings.json a un diccionario de python

    Returns:
        GlobalSettings: pbjeto con los settings sacados del archivo de configuracion settings.json
    """

    global _global_settings

    if _global_settings is None:
        with open("settings.json", "r") as tmp:
            json_gl = json.load(tmp)
            _global_settings = GlobalSettings(**json_gl)

    return _global_settings


def get_time() -> str:
    """Retorna el tiempo y hora actual

    Returns:
        srt: String Del Tiempo Actual
    """

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def key_split(key: str, split_ch:str = "_") -> Union[str, str]:
    """Separa las llaves de los diccionarios tipo nombre_id (implementado para que en los logs y json se puedan identificar
       con usuario o nombre)

    Args:
        key (str): _description_
        split_ch (str, optional): Caracter que separa la llave/valor. Defaults to "_".

    Returns:
        Union[str str]: [Llave separada, Valor separado]
    """

    i = 0
    for ch in key:
        if ch == split_ch:
            break
        i = i + 1

    return key[0:i], key[i+1:len(key)]

def to_object_id(id: int) -> bson.ObjectId:
    """Convierte un Id Int64 en ObjectId

    Args:
        id (int): Id a convertir

    Returns:
        bson.ObjectId: Id convertido en ObjectId
    """
    
    hex_string = hex(id)[2:].zfill(24)
    
    return bson.ObjectId(hex_string)