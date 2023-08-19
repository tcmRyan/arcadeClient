import json
import shutil
from pathlib import Path

from requests_mock import Mocker
import re

from client.main import generate_lists, download_games, cleanup, feed_updated_handler
from client.models import FeedModel, GameModel


def test_generate_lists(session):
    game1 = GameModel(
        id=1,
        name="Game1",
        version="1",
        game_uri="https://aws.com/my/bucket/1",
    )
    game2 = GameModel(
        id=2,
        name="Game2",
        version="1",
        game_uri="https://aws.com/my/bucket/2",
    )
    game2_updated = GameModel(
        id=2,
        name="Game2",
        version="2",
        game_uri="https://aws.com/my/bucket/2a",
    )
    game3 = GameModel(
        id=3,
        name="Game3",
        version="1",
        game_uri="https://aws.com/my/bucket/3",
    )
    session.add_all([game1, game2, game3])
    session.commit()

    original_feed = FeedModel(
        id=123,
        name="My Feed",
        description="Old Description",
        owner_id=1,
        games=[game1, game2],
    )
    session.add(original_feed)

    new_feed = FeedModel(
        id=123,
        name="My Feed",
        description="New one",
        owner_id=1,
        games=[game1, game2, game3],
    )

    # test new game
    result = generate_lists(new_feed, None)
    assert len(result.to_update) == 3
    assert len(result.to_delete) == 0

    # test new feed game
    result = generate_lists(new_feed, original_feed)
    assert len(result.to_update) == 1
    assert len(result.to_delete) == 0

    # test deleted feed game
    original_feed.games = [game1, game2, game3]
    new_feed.games = [game1, game2]
    result = generate_lists(new_feed, original_feed)
    assert len(result.to_update) == 0
    assert len(result.to_delete) == 1

    # test updated game
    original_feed.games = [game1, game2]
    new_feed.games = [game1, game2_updated]
    result = generate_lists(new_feed, original_feed)
    assert len(result.to_update) == 1
    assert len(result.to_delete) == 0


def test_download_games_and_cleanup(session):
    game1 = GameModel(
        id=1,
        name="Game1",
        version="1",
        game_uri="https://aws.com/my/bucket/1",
    )
    game2 = GameModel(
        id=2,
        name="Game2",
        version="1",
        game_uri="https://aws.com/my/bucket/2",
    )

    with Mocker() as m:
        matcher = re.compile("aws.com/my/bucket")
        m.register_uri("GET", matcher, json={"status": "ok"})
        download_games(1, [game1, game2])
        p = Path("./1")
        files = [f for f in p.glob("**/*") if f.is_file()]
        assert len(files) == 2

        cleanup("1", [game1])
        files = [f for f in p.glob("**/*") if f.is_file()]
        assert len(files) == 1
        shutil.rmtree(p)


def test_feed_update_handler(session, feed_message):
    with Mocker() as m:
        matcher = re.compile(".s3.amazonaws.com")
        m.register_uri("GET", matcher, json={"status": "ok"})
        feed_updated_handler(feed_message)

    data = json.loads(feed_message.payload)
    p = Path(f"./{data['id']}")
    files = [f for f in p.glob("**/*") if f.is_file()]
    assert len(files) == 2
    shutil.rmtree(p)
