import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from client.models import *


@pytest.fixture
def engine():
    engine = create_engine("sqlite:///:memory:")
    conn = engine.connect()
    yield engine
    conn.close()


@pytest.fixture
def session(engine):
    Base.metadata.create_all(engine)
    session = Session(bind=engine)
    yield session
    session.rollback()
    session.close()


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
    for i in range(5):
        game = GameModel(id=i, name=f"Game {i}", path=f"C:/some/path/{i}", version="2")
        games.append(game)

    session.add_all(games)
    session.commit()


@pytest.fixture
def feed(session, games):
    games = session.query(GameModel).all()
    feed = FeedModel(
        id=1, name="My Feed", games=games, description="Best Feed", owner_id=2
    )
    session.add(feed)
    session.commit()
