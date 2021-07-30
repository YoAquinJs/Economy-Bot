"""El módulo db_utils contiene metodos que acceden y modifican datos en la base de datos de MongoDB"""

from bson.objectid import ObjectId
from models.economy_user import EconomyUser
from models.enums import CollectionNames

from database.mongo_client import get_mongo_client

_mongo_client = get_mongo_client()


def insert(file: dict, database_name: str, collection: str):
    """Inserta un archivo a la base de datos de Mongo

        Args:
                file (dict): Diccionario con los datos de un log
                database_name (str): Nombre de la base de datos de mongo
                collection (str): Nombre de la colection a ingresar el archivo

        Returns:
                pymongo.results.InsertOneResult: Contiene la información de la inserción en MongoDB
    """

    return _mongo_client[database_name][collection].insert_one(file)


def modify(key: str, value, modify_key: str, modify_value, database_name: str, collection: str):
    """Modifica un archivo con la llave y valor especificados en la base de datos de Mongo

        Args:
                key (str): Llave a comparar
                value (indeterminado): Valor a comparar
                modify_key (dict): Nueva llave a cambiar
                modify_value (indeterminado): Nuevo valor a cambiar
                database_name (str): Nombre de la base de datos de mongo
                collection (str): Nombre de la colection a ingresar el archivo

        Returns:
                pymongo.results.UpdateOneResult: Contiene la información de la modificacion en MongoDB
    """

    return _mongo_client[database_name][collection].update_one({key: value}, {"$set": {modify_key: modify_value}})


def delete(key: str, value, database_name: str, collection: str):
    """Elimina un archivo en la base de datos de Mongo

        Args:
                key (str): Llave a comparar
                value (indeterminado): Valor a comparar
                database_name (str): Nombre de la base de datos de mongo
                collection (str): Nombre de la colection a ingresar el archivo

        Returns:
                pymongo.results.DeleteResult: Contiene la información de la eliminacion en MongoDB
    """

    return _mongo_client[database_name][collection].delete_one({key: value})


def query(key: str, value, database_name: str, collection: str):
    """Obtiene un archivo en la base de datos de Mongo

        Args:
                key (str): llave a buscar
                value (indeterminado): valor de la llave a buscar
                database_name (str): Nombre de la base de datos de mongo
                collection (str): Nombre de la colleccion en la cual se buscara el archivo

        Returns:
                dict: Archivo encontrado o None si no existe
    """

    return _mongo_client[database_name][collection].find_one({key: value})


def query_id(file_id: str, database_name: str, collection: str):
    """Obtiene un archivo por su id en la base de datos de Mongo

        Args:
                file_id (str): id del archivo
                database_name (str): Nombre de la base de datos de mongo
                collection (str): Nombre de la colleccion en la cual se buscara el archivo

        Returns:
                dict: Es un diccionario con la transacción o None si no la encuentra
    """

    try:
        return _mongo_client[database_name][collection].find_one({"_id": ObjectId(file_id)})
    except:
        return None


def query_all(database_name: str, collection: str):
    """Obtiene todos los archivos en la coleccion especificada en la base de datos de Mongo

        Args:
                database_name (str): Nombre de la base de datos de mongo
                collection (str): Nombre de la colleccion en la cual se buscara el archivo

        Returns:
                pymongo.cursor.Cursor: Clase iterable sobre Mongo query results de todos los archivos en la coleccion
    """

    return _mongo_client[database_name][collection].find({})


def exists(key: str, value, database_name: str, collection: str):
    """Revisa la existencia de un archivo en la base de datos de Mongo

        Args:
                key (str): Llave a comparar
                value (indeterminado): Valor a comparar
                database_name (str): Nombre de la base de datos de mongo
                collection (str): Nombre de la colleccion en la cual se buscara el archivo

        Returns:
                bool: Dice si existe en la db
    """
    doc = _mongo_client[database_name][collection].find_one({
        key: value
    }, {
        key: 1
    })

    if doc == None:
        return False

    return True


def get_random_user(database_name: str) -> EconomyUser:
    """Obtiene un _id aleatorio de un usuario en la base de datos de Mongo

        Args:
                database_name (str): Nombre de la base de datos de mongo
                collection (str): Nombre de la colleccion en la cual se buscara el archivo

        Returns:
                dict: Es un diccionario con la informacion del archivo
    """

    cursor = _mongo_client[database_name][CollectionNames.users.value].aggregate([
        {"$match": {"start_time": {"$exists": False}}},
        {"$sample": {"size": 1}}
    ])

    rnd_data = None
    for i in cursor:
        rnd_data = i

    random_user = EconomyUser(rnd_data['_id'], database_name)
    random_user.get_data_from_dict(rnd_data)
    return random_user


def delete_database_guild(database_name: str):
    _mongo_client.drop_database(database_name)
