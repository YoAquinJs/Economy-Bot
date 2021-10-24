import json
import datetime
import pytz

from models.global_settings import GlobalSettings

_global_settings = None


def get_global_settings() -> GlobalSettings:
    """Lee y parsea los settings.json a un diccionario de python

    Returns:
        dict: diccionario con los settings.json
    """

    global _global_settings

    if _global_settings is None:
        with open("settings.json", "r") as tmp:
            json_gl = json.load(tmp)
            _global_settings = GlobalSettings(**json_gl)

    return _global_settings


def get_time():
    """Retorna el tiempo y hora actual en UTC

    Returns:
        srt: String Del Tiempo Actual
    """

    return str(datetime.datetime.now(pytz.utc))


def key_split(key, split_ch="_"):
    """Separa las llaves de los diccionarios tipo nombre_id (implementado para que en los logs y json se puedan identificar
       con usuario o nombre)
    """

    i = 0
    for ch in key:
        if ch == split_ch:
            break
        i = i + 1

    return [key[0:i], key[i+1:len(key)]]


def round(num):
    str_num = str(num)
    dot_index = len(str_num)
    for i in range(len(str_num)):
        if str_num[i] == ".":
            dot_index = i
            break
    return float(str_num[0:dot_index + get_global_settings().max_decimals + 1])
