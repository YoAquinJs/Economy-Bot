"""El modulo mongo_client se encarga de la creacion del cliente de mongo y la conexion con la base de datos de Mongo"""

import pymongo
import certifi

from utils.utils import get_global_settings

global __mongo_client
__mongo_client = None


def init_database():
    """Inicializa el Cliente de la base de datos en el BonoboCluster de MongoDB

        Args:
                user (str): Usuario del Cluster de MongoDB
                password (str): Contraseña del usuario del Cluster de MongoDB
    """

    global __mongo_client

    # URL de la base de datos en Mongo Atlas
    global_settings = get_global_settings()
    url_db = f"mongodb+srv://{global_settings.mongoUser}:{global_settings.mongoPassword}"\
              "@cluster.jjdpmiv.mongodb.net/?retryWrites=true&w=majority"
    __mongo_client = pymongo.MongoClient(url_db, tlsCAFile=certifi.where())
    
    try:
        __mongo_client.admin.command('ping')
        print(f"data base initialized")
    except Exception as e:
        print(e)


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
