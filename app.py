from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import UserRegister, UserList, UserLogin
from resources.measurement import Measurement, MeasurementList
from db import db


app = Flask(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dbase.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "qwertyuiop"
app.secret_key = "qwertyuiop"
api = Api(app)

jwt = JWTManager(app)


@app.before_first_request
def create_tables():
    db.create_all()


api.add_resource(UserRegister, "/register")
api.add_resource(UserList, "/users")
api.add_resource(Measurement, "/measurement")
api.add_resource(MeasurementList, "/measurements/<string:location>")
api.add_resource(UserLogin, "/login")


if __name__ == "__main__":
    db.init_app(app)
    app.run(port=5000, debug=True)  # important to mention debug=True
