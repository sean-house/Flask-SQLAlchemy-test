from flask_restful import Resource, reqparse
from flask_jwt import jwt_required, current_identity
from security import hash_new_password, is_correct_password
from models.user import UserModel


class UserRegister(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="'username' field cannot be left blank!"
                        )
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="'password' field cannot be left blank!"
                        )

    def post(self):
        data = UserRegister.parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "User with that username already exists."}, 400
        pw_salt, pw_hash = hash_new_password(password=data['password'])
        this_user = UserModel(_id=None, username=data['username'], salt=pw_salt, hash=pw_hash)
        this_user.save_to_db()

        return {"message": "User created successfully."}, 201

    @jwt_required()
    def delete(self):
        """
        Remove user from database - but only for the same user as owns the token
        :param
        """
        data = UserRegister.parser.parse_args()
        print(f"Delete called by {current_identity.id}: {current_identity.username} with data: {data}")
        current_user = UserModel.find_by_id(current_identity.id)
        if current_user.username == data['username']:
            if is_correct_password(
                                    current_user.pw_salt,
                                    current_user.pw_hash,
                                    data['password']):
                current_user.delete_from_db()
                return {"message": f"User {current_user.username} deleted."}, 200
            else:
                return {"error": f"Invalid password"}, 401
        return {"error": f"You are only permitted to delete your own record"}, 401

class UserList(Resource):
    @jwt_required()
    def get(self):
        #return {'Users': list(map(lambda x: x.json(), UserModel.query.all()))}
        return {"users": [user.json() for user in UserModel.query.all()]}

