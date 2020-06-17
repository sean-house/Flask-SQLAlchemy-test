from db import db
from datetime import datetime
from models.user import UserModel
from typing import List


class MeasurementModel(db.Model):
    __tablename__ = "measures"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime(), nullable=False)
    location = db.Column(db.String(80), nullable=False)
    measurement = db.Column(db.String(80), nullable=False)
    value = db.Column(db.Float(precision=2), nullable=False)
    unit = db.Column(db.String(30), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel")

    # def __init__(
    #     self,
    #     timestamp: datetime,
    #     location: str,
    #     measurement: str,
    #     value: float,
    #     unit: str,
    #     user_id: int,
    # ):
    #     self.timestamp = timestamp
    #     self.location = location
    #     self.measurement = measurement
    #     self.value = value
    #     self.unit = unit
    #     self.user_id = user_id
    #
    # def json(self) -> MeasurementJSON:
    #     if self.user_id:
    #         username = UserModel.find_by_id(self.user_id).username
    #     else:
    #         username = "Not identified"
    #     return {
    #         "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
    #         "location": self.location,
    #         "measurement": self.measurement,
    #         "value": self.value,
    #         "unit": self.unit,
    #         "created by": username,
    #     }

    def save_to_db(self) -> None:
        """
        :cvar
        """
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        """
        :param
        """
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_location(cls, location) -> List["MeasurementModel"]:
        print(f"Find by location called for: {location}")
        return cls.query.filter_by(location=location).all()

    @classmethod
    def find_by_id(cls, _id) -> "MeasurementModel":
        return cls.query.filter_by(id=_id).first()
