from models.enums import BlackLists, CollectionNames
from database.db_utils import query, insert, delete


def user_in_black_list(user_id: str, black_list: str, database_name):
    if black_list == BlackLists.register.value:
        black_list = "register_bl"
    elif black_list == BlackLists.bug_report.value:
        black_list = "bugs_bl"
    elif black_list == BlackLists.shop.value:
        black_list = "shop_bl"
    elif black_list == BlackLists.transactions.value:
        black_list = "transactions_bl"

    return query("_id", user_id, database_name, CollectionNames.__getitem__(black_list).value)


def toggle_user_in_black_list(user_id: str, black_list: str, database_name):
    if black_list == BlackLists.register.value:
        black_list = "register_bl"
    elif black_list == BlackLists.bug_report.value:
        black_list = "bugs_bl"
    elif black_list == BlackLists.shop.value:
        black_list = "shop_bl"
    elif black_list == BlackLists.transactions.value:
        black_list = "transactions_bl"
    else:
        return None

    if user_in_black_list(user_id, black_list, database_name) is not None:
        delete("_id", int(user_id), database_name, CollectionNames.__getitem__(black_list).value)
        return "removido"
    else:
        insert({"_id": user_id}, database_name, CollectionNames.__getitem__(black_list).value)
        return "añadido"
