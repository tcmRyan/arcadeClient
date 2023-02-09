from paho.mqtt import client as mqtt
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QDialogButtonBox,
    QDialog,
)
import logging
import uuid

import click

from paho.mqtt.client import MQTTMessage

from client import session
from client.arcade_requests.api import Arcade
from client.models import DeviceModel, AuthModel

engine = None


class Window(QDialog):
    def __init__(self):
        super().__init__(parent=None)
        self.setWindowTitle("Arcade Share Application")
        self.setGeometry(100, 100, 400, 200)
        header = QLabel("<h1>Welcome to Arcade Share </h1>", parent=self)
        # helloMsg.move(60, 15)
        dialog_layout = QVBoxLayout()
        form_layout = QFormLayout()
        dialog_layout.addWidget(header)
        form_layout.addRow("Username: ", QLineEdit())
        form_layout.addRow("Password", QLineEdit())

        dialog_layout.addLayout(form_layout)
        buttons = QDialogButtonBox()
        buttons.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )

        dialog_layout.addWidget(buttons)

        self.setLayout(dialog_layout)


def on_message(client, userdata, message: MQTTMessage):
    if "game-updated" in message.topic:
        game_updated_handler(message)
    elif "feed-updated" in message.topic:
        feed_updated_handler(message)
    else:
        print(f"Unhandled topic: {message.topic}")


def game_updated_handler(message: MQTTMessage):
    pass


def feed_updated_handler(message: MQTTMessage):
    pass


def authenticate(config=False):
    auth = session.query(AuthModel).first()
    if auth is None or config:
        auth = AuthModel()
        auth.username = input("Arcade Share Username: ")
        auth.password = input("Arcade Share Password: ")
        auth.base_url = input("Arcade Share URL: ")
        api = Arcade(auth)
        resp = api.auth.post()
        if resp.status_code > 200:
            authenticate(True)


def provision_device(config=False):
    auth = session.query(AuthModel).first()
    device = session.query(DeviceModel).first()
    if device is None:
        device = DeviceModel()
        config = True
    device.mac = hex(uuid.getnode())
    device.active = True
    if config:
        device.name = input("Please name your device: ")
        session.add(device)
        session.commit()
        api = Arcade(auth)
        resp = api.device.create(device)
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
    authenticate(config=config)
    provision_device(config=config)
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttc.username_pw_set("DemoAdmin", "temp1234")
    mqttc.enable_logger(logger=logger)
    mqttc.connect(host="127.0.0.1", port=1883, keepalive=60, bind_address="")
    mqttc.subscribe("test/topic")
    logger.info("starting")
    mqttc.loop_forever()


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    logger = logging.Logger(
        __name__,
        level=logging.DEBUG,
    )
    configure()
