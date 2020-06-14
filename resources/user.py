from typing import Tuple
import os
import hashlib
import hmac
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required,
    jwt_refresh_token_required,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
)
from models.user import UserModel
import messages.en as msgs

_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    "username", type=str, required=True, help=msgs.BLANK_FIELD.format('username')
)
_user_parser.add_argument(
    "password", type=str, required=True, help=msgs.BLANK_FIELD.format('password')
)


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


def authenticate(username, password) -> 'UserModel':
    this_user = UserModel.find_by_username(username)
    print(f"Calling Authenticate: User found = {username}")
    if this_user and is_correct_password(
        this_user.pw_salt, this_user.pw_hash, password
    ):
        # if user and safe_str_cmp(user.password, password):
        return this_user


class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data["username"]):
            return {"message": msgs.USER_EXISTS}, 400
        pw_salt, pw_hash = hash_new_password(password=data["password"])
        this_user = UserModel(
            _id=None, username=data["username"], salt=pw_salt, hash=pw_hash
        )
        this_user.save_to_db()

        return {"message": msgs.CREATED.format('User')}, 201

    @jwt_required
    def delete(self):
        """
        Remove user from database - but only for the same user as owns the token
        :param
        """
        data = _user_parser.parse_args()
        current_identity = get_jwt_identity()
        current_user = UserModel.find_by_id(current_identity)
        print(
            f"Delete called by {current_user.id}: {current_user.username} with data: {data}"
        )
        if current_user.username == data["username"]:
            if is_correct_password(
                current_user.pw_salt, current_user.pw_hash, data["password"]
            ):
                current_user.delete_from_db()
                return {"message": msgs.DELETED.format(current_user.username)}, 200
            else:
                return {"error": msgs.INVALID_PASSWORD}, 401
        return {"error": msgs.OWN_RECORD_ONLY}, 401


class UserLogin(Resource):
    def post(self):
        data = _user_parser.parse_args()

        this_user = UserModel.find_by_username(data["username"])

        # this is what the `authenticate()` function did in security.py
        if this_user and is_correct_password(
            this_user.pw_salt, this_user.pw_hash, data["password"]
        ):
            # identity= is what the identity() function did in security.py—now stored in the JWT
            access_token = create_access_token(identity=this_user.id, fresh=True)
            refresh_token = create_refresh_token(this_user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        return {"message": msgs.INVALID_PASSWORD}, 401


class UserList(Resource):
    @jwt_required
    def get(self):
        # return {'Users': list(map(lambda x: x.json(), UserModel.query.all()))}
        return {"users": [user.json() for user in UserModel.find_all()]}


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_identity = get_jwt_identity()
        access_token = create_access_token(identity=current_identity, fresh=False)
        refresh_token = create_refresh_token(current_identity)
        return {"access_token": access_token, "refresh_token": refresh_token}, 200