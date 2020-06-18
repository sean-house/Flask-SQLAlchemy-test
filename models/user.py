import os
from flask import request, url_for
from requests import Response, post
from db import db
from typing import List, Union

import messages.en as msgs


MAIL_DOMAIN = 'mg.housesofyateley.net'
MAILGUN_API_BASEURL = 'https://api.eu.mailgun.net/v3/{}'.format(MAIL_DOMAIN)
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY', None)

class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    pw_salt = db.Column(db.LargeBinary(80))
    pw_hash = db.Column(db.LargeBinary(100))
    activated = db.Column(db.Boolean(), default=False)


    def save_to_db(self) -> None:
        """
        Save the User record to the database
        """
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        """
        Delete the user record from the database
        """
        db.session.delete(self)
        db.session.commit()

    def send_confirmation_email(self) -> Union[Response, None]:
        """
        Send an address confirmation email to the user
        """
        link = request.url_root[:-1] + url_for('userconfirm', user_id=self.id)
        if MAILGUN_API_KEY:
            return post(
                    MAILGUN_API_BASEURL + "/messages",
                    auth=("api", MAILGUN_API_KEY),
                    data={
                        "from": f"{msgs.FROM_TITLE} <{msgs.FROM_EMAIL}>",
                        "to": self.email,
                        "subject": msgs.MAIL_SUBJECT,
                        "text": msgs.MAIL_BODY.format(self.username, link)
                    })
        else:
            print(f"No Mailgun API key in environment - cannot send confirmation email to {self.email}")
            return None


    @classmethod
    def find_all(cls) -> List['UserModel']:
        """
        :param
        """
        return cls.query.all()

    @classmethod
    def find_by_username(cls, username) -> 'UserModel':
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id) -> 'UserModel':
        return cls.query.filter_by(id=_id).first()
