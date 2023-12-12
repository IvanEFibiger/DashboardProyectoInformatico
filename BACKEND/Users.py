class User:
    def __init__(self, row):
        self._user_id = row[0]
        self._user = row[1]
        self._email = row[2]

    def to_dict(self):
        return {
            'user_id': self._user_id,
            'user': self._user,
            'email': self._email,
        }