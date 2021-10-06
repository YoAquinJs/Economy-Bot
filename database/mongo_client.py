"""El módulo mongo_client se encarga de la creacion del cliente de mongo y la conexion con la base de datos de Mongo"""

import pymongo
import certifi

from utils.utils import get_global_settings

__mongo_client = None
global_settings = get_global_settings()


def init_database():
    """Inicializa el Cliente de la base de datos en el BonoboCluster de MongoDB

        Args:
                user (str): Usuario del Cluster de MongoDB
                password (str): Contraseña del usuario del Cluster de MongoDB
    """

    global __mongo_client

    # URL de la base de datos en Mongo Atlas
    url_db = f"mongodb+srv://{global_settings.mongoUser}:{global_settings.mongoPassword}" \
             f"@bonobocluster.dl8wg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
    __mongo_client = pymongo.MongoClient(url_db, tlsCAFile=certifi.where())


def get_mongo_client() -> pymongo.MongoClient:
    """Esta función retorna un singleton de pymongo.MongoClient

        Returns:
                pymongo.MongoClient: Cliente para conectarse a una base de datos de MongoDB
    """

    if __mongo_client is None:
        init_database()

    return __mongo_client


def close_client():
    """Desconecta el cliente de MongoDB
    """

    get_mongo_client().close()
    print('Mongo Client Closed')
