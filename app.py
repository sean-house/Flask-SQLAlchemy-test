from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError
import os

from resources.user import UserRegister, UserList, UserLogin, TokenRefresh
from resources.measurement import Measurement, MeasurementList
from db import db
from ma import ma


app = Flask(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "FLASK_DB_URL", "sqlite:///dbase.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "qwertyuiop"
app.secret_key = "qwertyuiop"
api = Api(app)

jwt = JWTManager(app)


@app.before_first_request
def create_tables():
    db.create_all()


@app.errorhandler(ValidationError)
def handle_marshmallow_error(err):
    return jsonify(err.messages), 400


api.add_resource(UserRegister, "/register")
api.add_resource(UserList, "/users")
api.add_resource(Measurement, "/measurement")
api.add_resource(MeasurementList, "/measurements/<string:location>")
api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")


if __name__ == "__main__":
    db.init_app(app)
    ma.init_app(app)
    app.run(port=5000, debug=True)  # important to mention debug=True
