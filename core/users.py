from typing import List

from models.economy_user import EconomyUser
from models.enums import CollectionNames
from database.mongo_client import get_mongo_client


def get_users_starting_with(search: str, database_name: str) -> List[EconomyUser]:
    mclient = get_mongo_client()
    coll = mclient[database_name][CollectionNames.users.value]

    users = []
    results = coll.find({
        'name': {'$regex': f'^{search}', '$options' :'i'}
    })

    for result in results:
        user = EconomyUser(-1, database_name=database_name)
        user.get_data_from_dict(result)

        users.append(user)

    return users
