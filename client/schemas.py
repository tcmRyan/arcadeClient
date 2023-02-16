from marshmallow import EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from client.models import DeviceModel, AuthModel, FeedModel, GameModel


class DeviceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DeviceModel
        include_relationships = True
        load_instance = True
        unknown = EXCLUDE


class AuthSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AuthModel
        unknown = EXCLUDE


class FeedSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = FeedModel
        include_relationships = True
        load_instance = True
        unknown = EXCLUDE


class GameSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = GameModel
        include_relationships = True
        load_instance = True
