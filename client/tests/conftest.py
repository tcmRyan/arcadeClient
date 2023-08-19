import json
from collections import namedtuple

import pytest

from client import db
from client.models import *
from client.schemas import BaseSchema


@pytest.fixture
def session():
    db.config("sqlite:///:memory:")
    Base.metadata.create_all(db.engine)
    BaseSchema.session = db.session

    yield db.session
    db.session.rollback()
    db.session.close()


@pytest.fixture
def device(session):
    device = DeviceModel(
        id=3,
        name="my device",
        active=True,
    )
    session.add(device)
    session.commit()


@pytest.fixture
def games(session):
    games = []
    for i in range(1000, 1005):
        game = GameModel(
            id=i, name=f"Game {i}", game_uri=f"https://aws.com/bucket/{i}", version="2"
        )
        games.append(game)

    db.session.add_all(games)
    db.session.commit()
    return games


@pytest.fixture
def feed(session, games):
    feed = FeedModel(
        id=1, name="My Feed", games=games, description="Best Feed", owner_id=2
    )
    db.session.add(feed)
    db.session.commit()


@pytest.fixture
def feed_message():
    message = namedtuple("Message", "payload")
    payload = json.dumps(
        {
            "name": "My Feed123",
            "owner_id": 4,
            "description": "A new game feed",
            "games": [
                {
                    "name": "qweqwe",
                    "bucket": "qweqwe/arcade-sdf_5.uf2",
                    "thumbnail_uri": "https://tenant-19.s3.amazonaws.com/qweqwe/FB_IMG_1664567803276.jpg?AWSAccessKeyId"
                    "=AKIAY7B45HPWDL5YQRIP&Signature=tsYCfbYNfvOAZQp0sFOxTDqR5gE%3D&Expires=1676674936",
                    "thumbnail": "qweqwe/FB_IMG_1664567803276.jpg",
                    "description": "qweqwe",
                    "version": 1,
                    "id": 1,
                    "game_uri": "https://tenant-19.s3.amazonaws.com/qweqwe/arcade-sdf_5.uf2?AWSAccessKeyId"
                    "=AKIAY7B45HPWDL5YQRIP&Signature=LuZzSt7w5qe03VcnGIAbtJ%2FFUPk%3D&Expires=1676674937",
                },
                {
                    "name": "New Game",
                    "bucket": "New Game/arcade-sdf_1.uf2",
                    "thumbnail_uri": "https://tenant-19.s3.amazonaws.com/New%20Game/16906368708_a9bca2a354_b.jpg"
                    "?AWSAccessKeyId=AKIAY7B45HPWDL5YQRIP&Signature=COuqsEE0NNlc6SVJa%2FUsOk21JME%3D"
                    "&Expires=1676674937",
                    "thumbnail": "New Game/16906368708_a9bca2a354_b.jpg",
                    "description": "sadf",
                    "version": 1,
                    "id": 2,
                    "game_uri": "https://tenant-19.s3.amazonaws.com/New%20Game/arcade-sdf_1.uf2?AWSAccessKeyId"
                    "=AKIAY7B45HPWDL5YQRIP&Signature=JOKMRhF4%2Bw0V9D2K4GBINHxSjlg%3D&Expires=1676674937",
                },
            ],
            "id": 6,
        }
    )
    return message(payload)
