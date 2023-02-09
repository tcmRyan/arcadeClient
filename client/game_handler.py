from sqlalchemy import select
from sqlalchemy.orm import Session

from client.main import engine
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
            .where(FeedModel.id == device.current_feed.id)
            .where(GameModel.id == self.message.get("id"))
        )
        with Session(engine) as session:
            session.scalars(stmt).one()
