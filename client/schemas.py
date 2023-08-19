from marshmallow import EXCLUDE, fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from client.models import DeviceModel, AuthModel, FeedModel, GameModel
from client import db


class BaseSchema(SQLAlchemyAutoSchema):
    class Meta:
        sqla_session = db.session


class DeviceSchema(BaseSchema):
    class Meta:
        model = DeviceModel
        include_relationships = True
        load_instance = True
        unknown = EXCLUDE


class AuthSchema(BaseSchema):
    class Meta:
        model = AuthModel
        unknown = EXCLUDE


class GameSchema(BaseSchema):
    class Meta:
        model = GameModel
        include_relationships = True
        load_instance = True
        unknown = EXCLUDE


class FeedSchema(BaseSchema):
    games = fields.Nested(GameSchema, many=True)

    class Meta:
        model = FeedModel
        include_relationships = True
        load_instance = True
        unknown = EXCLUDE
