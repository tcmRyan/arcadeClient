from sqlalchemy import select

from client import DB, default_connection
from models import GameModel, FeedModel, DeviceModel


class GameHandler:
    def __init__(self, message, topic):
        self.message = message
        self.topic = topic

    def update_handler(self):
        device = select(DeviceModel).first()
        stmt = (
            select(GameModel)
            .join(FeedModel)
            .where(FeedModel.id == device.feed.id)
            .where(GameModel.id == self.message.get("id"))
        )
        with DB(default_connection) as db:
            db.session.scalars(stmt).one()
