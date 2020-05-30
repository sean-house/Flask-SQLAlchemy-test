from typing import Tuple
import os
import hashlib
import hmac
from models.user import UserModel


def hash_new_password(password: str) -> Tuple[bytes, bytes]:
    """
    Hash the provided password with a randomly-generated salt and return the
    salt and hash to store in the database.
    """
    salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt, pw_hash

def is_correct_password(salt: bytes, pw_hash: bytes, password: str) -> bool:
    """
    Given a previously-stored salt and hash, and a password provided by a user
    trying to log in, check whether the password is correct.
    """
    return hmac.compare_digest(
        pw_hash,
        hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    )

# Example usage:
# salt, pw_hash = hash_new_password('correct horse battery staple')
# print(f"Salt: {salt}, hash: {pw_hash}")
# assert is_correct_password(salt, pw_hash, 'correct horse battery staple')
# assert not is_correct_password(salt, pw_hash, 'Tr0ub4dor&3')
# assert not is_correct_password(salt, pw_hash, 'rosebud')


def authenticate(username, password):
    this_user = UserModel.find_by_username(username)
    print(f"Calling Authenticate: User found = {username}")
    if this_user and is_correct_password(this_user.pw_salt, this_user.pw_hash, password):
    # if user and safe_str_cmp(user.password, password):
        return this_user


def identity(payload):
    user_id = payload['identity']
    return UserModel.find_by_id(user_id)