from typing import Tuple
import logging
import os
import hashlib
import hmac
import json
import traceback
from flask_restful import Resource
from flask import request, make_response, render_template
from flask_jwt_extended import (
    jwt_required,
    jwt_refresh_token_required,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
)
from models.user import UserModel
from schemas.user import UserSchema
from libs.mailgun import MailGunException
import messages.en as msgs


user_schema = UserSchema()


def hash_new_password(password: str) -> Tuple[bytes, bytes]:
    """
    Hash the provided password with a randomly-generated salt and return the
    salt and hash to store in the database.
    """
    salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt, pw_hash


def is_correct_password(salt: bytes, pw_hash: bytes, password: str) -> bool:
    """
    Given a previously-stored salt and hash, and a password provided by a user
    trying to log in, check whether the password is correct.
    """
    return hmac.compare_digest(
        pw_hash, hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    )


def authenticate(username, password) -> "UserModel":
    this_user = UserModel.find_by_username(username)
    print(f"Calling Authenticate: User found = {username}")
    if this_user and is_correct_password(
        this_user.pw_salt, this_user.pw_hash, password
    ):
        return this_user


class UserRegister(Resource):
    def post(self):
        user = user_schema.load(request.get_json())
        logging.info(f"USER REGISTER:  Passed user= {user}")

        if UserModel.find_by_username(user["username"]):
            return {"message": msgs.USER_EXISTS}, 400
        if UserModel.find_by_email(user["email"]):
            return {"message": msgs.EMAIL_EXISTS}, 400

        pw_salt, pw_hash = hash_new_password(password=user["password"])
        this_user = UserModel(
            id=None,
            username=user["username"],
            email=user["email"],
            pw_salt=pw_salt,
            pw_hash=pw_hash,
        )
        try:
            this_user.save_to_db()
            resp = this_user.send_confirmation_email()
            if resp:
                logging.info(f"USER: Confirmation email sent: {json.loads(resp.text)['id']}")
            return {"message": msgs.CREATED.format(this_user.username)}, 201
        except MailGunException as e:
            logging.error(f"USER: Mailgun exception caught: {str(e)}")
            this_user.delete_from_db()
            return {"error": msgs.FAILED_TO_MAIL.format(this_user.email)}, 500
        except Exception as e:
            logging.error(f"USER REGISTER: Other exception: {str(e)}")
            traceback.print_exc()
            this_user.delete_from_db()
            return {"error": msgs.FAILED_TO_CREATE.format(str(e))}, 500

    @jwt_required
    def delete(self):
        """
        Remove user from database - but only for the same user as owns the token
        :param
        """
        user = user_schema.load(request.get_json(), partial=("email",))

        current_identity = get_jwt_identity()
        db_user = UserModel.find_by_id(current_identity)
        logging.info(
            f"Delete called by {db_user.id}: {db_user.username} with data: {user.username}"
        )
        if db_user.username == user.username:
            if is_correct_password(db_user.pw_salt, db_user.pw_hash, user.password):
                db_user.delete_from_db()
                return {"message": msgs.DELETED.format(db_user.username)}, 200
            else:
                return {"error": msgs.INVALID_PASSWORD}, 401
        return {"error": msgs.OWN_RECORD_ONLY}, 401


class UserLogin(Resource):
    def post(self):
        login_user = user_schema.load(
            request.get_json(), partial=("email",)
        )  # Login user is a dict
        this_user = UserModel.find_by_username(login_user["username"])
        # now check the user model returned from the login has the same password as the database user
        if this_user and is_correct_password(
            this_user.pw_salt, this_user.pw_hash, login_user["password"]
        ):
            if this_user.activated:
                access_token = create_access_token(identity=this_user.id, fresh=True)
                refresh_token = create_refresh_token(this_user.id)
                return (
                    {"access_token": access_token, "refresh_token": refresh_token},
                    200,
                )
            else:
                return {"message": msgs.NOT_CONFIRMED.format(this_user.username)}, 400

        return {"message": msgs.INVALID_PASSWORD}, 401


class UserList(Resource):
    @jwt_required
    def get(self):
        return {"users": [user_schema.dump(user) for user in UserModel.find_all()]}


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_identity = get_jwt_identity()
        access_token = create_access_token(identity=current_identity, fresh=False)
        refresh_token = create_refresh_token(current_identity)
        logging.info(f"REFRESH: Token refreshed for UserID {current_identity}")
        return {"access_token": access_token, "refresh_token": refresh_token}, 200


class UserConfirm(Resource):
    @classmethod
    def get(cls, user_id: int):
        """
        :var
        """
        user = UserModel.find_by_id(user_id)
        if user:
            user.activated = True
            user.save_to_db()
            headers = {"Content-Type": "text/html"}
            return make_response(
                render_template("confirmation_page.html", email=user.email),
                202,
                headers,
            )
        else:
            return {"messages": msgs.USER_NONEXISTANT.format(user_id)}, 404
