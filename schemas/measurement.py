from ma import ma
from models.measurement import MeasurementModel
from models.user import UserModel
from schemas.user import UserSchema


class MeasurementSchema(ma.SQLAlchemyAutoSchema):
    user = ma.Nested(UserSchema)

    class Meta:
        model = MeasurementModel
        load_only = ("user",)
        dump_only = ("id",)
        include_fk = True
        load_instance = True
