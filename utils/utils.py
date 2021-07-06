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
