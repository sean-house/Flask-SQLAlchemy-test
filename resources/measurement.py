from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.measurement import MeasurementModel
from schemas.measurement import MeasurementSchema
import messages.en as msgs

measurement_schema = MeasurementSchema()
measurement_list_schema = MeasurementSchema(many=True)


class Measurement(Resource):
    @jwt_required
    def post(self):
        measurement_json = request.get_json()
        print(measurement_json)
        measurement_json["user_id"] = get_jwt_identity()
        this_measurement = measurement_schema.load(measurement_json)

        # this_measurement = MeasurementModel(
        #     timestamp=data["timestamp"],
        #     location=data["location"],
        #     measurement=data["measurement"],
        #     value=data["value"],
        #     unit=data["unit"],
        #     user_id=current_identity,
        # )
        this_measurement.save_to_db()

        return (
            {
                "message": msgs.MEASUREMENT_STORED,
                "data": measurement_schema.dump(this_measurement),
            },
            201,
        )


class MeasurementList(Resource):
    @jwt_required
    def get(self, location):
        return {
            "data": measurement_list_schema.dump(
                MeasurementModel.find_by_location(location)
            )
        }
