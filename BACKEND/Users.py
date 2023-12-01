class User:
    def __init__(self, row):
        self._user = row[0]
        self._email = row[1]


        def to_dict(self):
            return {
                'user_id': self.user_id,
                'user': self.user,
                'email': self.email,

            }