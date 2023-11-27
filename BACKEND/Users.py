class User:
    def __init__(self, row):
        self._user = user
        self._email = email
        self._password = password

        def to_dict(self):
            return {
                'user_id': self.user_id,
                'user': self.user,
                'email': self.email,
                'password': self.password  # Recuerda que esto no es seguro en producción
            }