"""El modulo db_utils provee metodos CRUD para gestionar la base de datos de MongoDB"""

from models.enums import CollectionNames
from database.mongo_client import get_mongo_client

_mongo_client = get_mongo_client()


def insert(file: dict, database_name: str, collection: str):
    """Inserta un archivo a la base de datos de Mongo

        Args:
                file (dict): Diccionario con los datos del registro
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


def delete_all(database_name: str, collection: str):
    """Elimina un archivo en la base de datos de Mongo

        Args:
                key (str): Llave a comparar
                value (indeterminado): Valor a comparar
                database_name (str): Nombre de la base de datos de mongo
                collection (str): Nombre de la colection a ingresar el archivo

        Returns:
                pymongo.results.DeleteResult: Contiene la información de la eliminacion en MongoDB
    """

    return _mongo_client[database_name][collection].delete_many({})


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

    try:
        return _mongo_client[database_name][collection].find_one({key: value})
    except:
        return None


def query_all(database_name: str, collection: str):
    """Obtiene todos los archivos en la coleccion especificada en la base de datos de Mongo

        Args:
                database_name (str): Nombre de la base de datos de mongo
                collection (str): Nombre de la colleccion en la cual se buscara el archivo

        Returns:
                pymongo.cursor.Cursor: Clase iterable sobre los Mongo query results de todos los archivos en la coleccion
    """

    return _mongo_client[database_name][collection]


def exists(key: str, value, database_name: str, collection: str):
    """Revisa la existencia de un archivo en la base de datos de Mongo

        Args:
                key (str): Llave a comparar
                value (indeterminado): Valor a comparar
                database_name (str): Nombre de la base de datos de mongo
                collection (str): Nombre de la colleccion en la cual se buscara el archivo

        Returns:
                bool: Existencia en la db
    """
    
    doc = _mongo_client[database_name][collection].find_one({key: value}, {key: 1})

    return doc != None


def delete_database_guild(database_name: str):
    """Elimina la base de datos de un servidor de discord

        Args:
                database_name (str): Nombre_ID de la base de datos del servidor de discord
    """
    
    _mongo_client.drop_database(database_name)
