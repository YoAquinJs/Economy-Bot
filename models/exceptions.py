class NotFoundEconomyUser(Exception):
    def __init__(self, message):
        self.message = message


class RegisteredUser(Exception):
    def __init__(self, message):
        self.message = message
