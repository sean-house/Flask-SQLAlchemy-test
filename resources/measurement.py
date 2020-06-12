from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.measurement import MeasurementModel
from datetime import datetime
import messages.en as msgs


class Measurement(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        "timestamp",
        type=lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"),
        required=True,
        help=msgs.BLANK_FIELD.format('timestamp'),
    )
    parser.add_argument(
        "location",
        type=str,
        required=True,
        help=msgs.BLANK_FIELD.format('location'),
    )
    parser.add_argument(
        "measurement",
        type=str,
        required=True,
        help=msgs.BLANK_FIELD.format('measurement'),
    )
    parser.add_argument(
        "value", type=float, required=True, help=msgs.BLANK_FIELD.format('value'),
    )
    parser.add_argument(
        "unit", type=str, required=True, help=msgs.BLANK_FIELD.format('unit')
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

        return {"message": msgs.MEASUREMENT_STORED, "data": this_measurement.json()}, 201


class MeasurementList(Resource):

    @jwt_required
    def get(self, location):
        measurement_list = MeasurementModel.find_by_location(location)

        return {"data": [msmt.json() for msmt in measurement_list]}
