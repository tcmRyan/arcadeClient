import json
from collections import namedtuple
from pathlib import Path

import requests
from marshmallow import ValidationError
from paho.mqtt import client as mqtt

import logging
import uuid

import click

from paho.mqtt.client import MQTTMessage

from client import db, default_connection
from client.arcade_requests.api import Arcade
from client.models import DeviceModel, AuthModel, GameModel, FeedModel
from client.schemas import FeedSchema


def on_message(client, userdata, message: MQTTMessage):
    if "feeds/updated" in message.topic:
        feed_updated_handler(message)
    else:
        print(f"Unhandled topic: {message.topic}")


def game_filter(game: GameModel, existing_games):
    existing = existing_games.get(game.id)
    if existing is None or existing.version != game.version:
        return True


Feeds = namedtuple("Feeds", "to_update to_delete")


def generate_lists(data: FeedModel, feed: FeedModel | None) -> Feeds:
    if feed and data.id == feed.id:
        existing_games = {game.id: game for game in feed.games}
        new_games = [game.id for game in data.games]
        game_update_list = [
            game for game in data.games if game_filter(game, existing_games)
        ]
        delete_games = [game for game in feed.games if game.id not in new_games]
    else:
        game_update_list = data.games
        delete_games = []

    return Feeds(game_update_list, delete_games)


def feed_updated_handler(message: MQTTMessage):
    schema = FeedSchema()
    try:
        data = json.loads(message.payload)
        data = schema.load(data)
    except ValidationError as err:
        print(err.messages)
        print(err.valid_data)
        return
    feed = db.session.query(DeviceModel).first()

    feeds = generate_lists(data, feed)

    download_games(data.id, feeds.to_update)
    db.session.add(data)
    db.session.commit()
    if feed is not None:
        cleanup(feed.id, feeds.to_delete)


def cleanup(fid, games: list[GameModel]):
    p = Path(f"./{fid}")
    for game in games:
        print(f"removing {game.name}")
        path = p.joinpath(game.name + ".uf2")
        path.unlink(missing_ok=True)


def download_games(fid, games: list[GameModel]):
    p = Path(f"./{fid}")
    p.mkdir(parents=True, exist_ok=True)
    for game in games:
        r = requests.get(game.game_uri)
        with open(p.joinpath(game.name + ".uf2"), "wb") as f:
            f.write(r.content)
        print(f"Saved {game.name}")
    print("Download for feed completed")


def authenticate(config=False):
    auth = db.session.query(AuthModel).first()
    if auth is None:
        auth = AuthModel()
        config = True
    if config:
        auth.username = input("Arcade Share Username: ")
        auth.password = input("Arcade Share Password: ")
        auth.base_url = input("Arcade Share URL: ")
        db.session.add(auth)
        db.session.commit()
        api = Arcade(auth)
        resp = api.auth.post()
        if resp.status_code > 200:
            authenticate(True)


def provision_device(config=False):
    auth = db.session.query(AuthModel).first()
    device = db.session.query(DeviceModel).first()
    create = False
    if device is None:
        device = DeviceModel()
        config = True
        create = True
    device.mac = hex(uuid.getnode())
    device.active = True
    if config:
        device.name = input("Please name your device: ")
        db.session.add(device)
        db.session.commit()
        api = Arcade(auth)
        if create:
            resp = api.device.create(device)
        else:
            resp = api.device.update(device)
        if resp.status_code == 200:
            print("Device successfully registered")
        else:
            print(
                f"Received a {resp.status_code} response with the message: {resp.content}"
            )


@click.command()
@click.option(
    "--config", "-c", is_flag=True, help="Enter configuration before running program"
)
def configure(config):
    db.conn_str = default_connection
    db.create_session()
    authenticate(config=config)
    provision_device(config=config)
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    auth = db.session.query(AuthModel).first()
    mqttc.username_pw_set(auth.username, auth.password)
    mqttc.enable_logger(logger=logger)
    mqttc.connect(host="127.0.0.1", port=1883, keepalive=60, bind_address="")
    mqttc.subscribe(f"{auth.tenant_id}/feeds/updated")
    mqttc.subscribe(f"{auth.tenant_id}/devices/updated")
    mqttc.subscribe(f"{auth.tenant_id}/games/updated")
    logger.info("starting")
    mqttc.loop_forever()


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    logger = logging.Logger(
        __name__,
        level=logging.DEBUG,
    )
    configure()
