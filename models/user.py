from db import db


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    pw_salt = db.Column(db.String(80))
    pw_hash = db.Column(db.String(100))

    def __init__(self, _id, username, salt, hash):
        self.id = _id
        self.username = username
        self.pw_salt = salt
        self.pw_hash = hash

    def json(self):
        return {"id": self.id, "username": self.username}

    def save_to_db(self):
        """
        :cvar
        """
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        """
        :param
        """
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()
