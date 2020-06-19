from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError
import os
import sys

from resources.user import UserRegister, UserList, UserLogin, TokenRefresh, UserConfirm
from resources.measurement import Measurement, MeasurementList
from db import db
from ma import ma


app = Flask(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "FLASK_DB_URL", "sqlite:///dbase.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
secret_key = os.environ.get('FLASK_SECRET', "qwertyuiop")
app.config["JWT_SECRET_KEY"] = secret_key
app.secret_key = secret_key
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
api.add_resource(UserConfirm, "/confirm/<int:user_id>")


if __name__ == "__main__":
    db.init_app(app)
    ma.init_app(app)
    intent = os.environ.get('FLASK_INTENT', None)
    if intent == 'dev':
        print('Running with "dev" environment')
        app.run(port=5000, debug=True, use_reloader=False)  # important to mention debug=True
    elif intent == 'prod':
        print('Running with "prod" environment')
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print('ERROR:  No FLASK_INTENT environment variable')
        sys.exit(-1)

