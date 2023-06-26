"""Este modulo contiene excepciones que pueden surgir en procesos de la aplicacion"""

class NotFoundEconomyUser(Exception):
    """Ocurre cuando el usuario no se encuntra en la base de datos"""
    
    def __init__(self, message):
        self.message = message


class RegisteredUser(Exception):
    def __init__(self, message):
        self.message = message
