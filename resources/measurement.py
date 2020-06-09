from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.measurement import MeasurementModel
from datetime import datetime


class Measurement(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        "timestamp",
        type=lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"),
        required=True,
        help="'timestamp' field cannot be left blank!",
    )
    parser.add_argument(
        "location",
        type=str,
        required=True,
        help="'location' field cannot be left blank!",
    )
    parser.add_argument(
        "measurement",
        type=str,
        required=True,
        help="'measurement' field cannot be left blank!",
    )
    parser.add_argument(
        "value", type=float, required=True, help="'value' field cannot be left blank!"
    )
    parser.add_argument(
        "unit", type=str, required=True, help="'unit' field cannot be left blank!"
    )

    @jwt_required
    def post(self):
        data = Measurement.parser.parse_args()
        current_identity = get_jwt_identity()

        this_measurement = MeasurementModel(
            timestamp=data["timestamp"],
            location=data["location"],
            measurement=data["measurement"],
            value=data["value"],
            unit=data["unit"],
            user_id=current_identity,
        )
        this_measurement.save_to_db()

        return {"message": "Measurement stored", "data": this_measurement.json()}, 201


class MeasurementList(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        "location",
        type=str,
        required=True,
        help="'location' field must be specified to retrieve measurements!",
    )

    @jwt_required
    def get(self, location):
        data = MeasurementList.parser.parse_args()
        measurement_list = MeasurementModel.find_by_location(data["location"])

        return {"data": [msmt.json() for msmt in measurement_list]}
