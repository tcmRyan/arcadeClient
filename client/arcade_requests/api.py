from requests import Response

from client.arcade_requests.arc_requests import ArcRequest
from client import db
from client.models import AuthModel, DeviceModel, FeedModel, GameModel
from client.schemas import DeviceSchema, AuthSchema, FeedSchema


class Arcade:
    def __init__(self, auth: AuthModel):
        self.requests = ArcRequest(auth)
        self._authModel = auth
        self.auth = AuthenticationApi(self.requests, auth)
        self.device = Device(self.requests)
        self.feed = Feed(self.requests)
        self.game = Game(self.requests)


class AuthenticationApi:
    def __init__(self, requests: ArcRequest, auth: AuthModel):
        self.requests = requests
        self.auth = auth

    def post(self):
        payload = {
            "username": self.auth.username,
            "password": self.auth.password,
        }
        resp = self.requests.post(
            "/auth/user-login",
            json=payload,
        )

        if resp.status_code in [200, 201]:
            data = resp.json()
            # TODO: Serialize better
            self.auth.access_token = data["access_token"]
            self.auth.refresh_token = data["refresh_token"]
            self.auth.tenant_id = data["user"]["tenant_id"]
            db.session.add(self.auth)
            db.session.commit()
        else:
            print(f"{resp.status_code}: {resp.content}")
        return resp


class Device:
    rel = "/api/devices"

    def __init__(self, requests):
        self.requests = requests

    def list(self):
        self.requests.get(self.rel)

    def create(self, device: DeviceModel) -> Response:
        payload = DeviceSchema(exclude=["feed"]).dump(device)
        return self.requests.post(self.rel, json=payload)

    def get(self, device: DeviceModel):
        return self.requests.get(self.rel + f"/{device.id}")

    def update(self, device: DeviceModel):
        payload = DeviceSchema(exclude=["feed"]).dump(device)
        resp = self.requests.put(
            self.rel + f"/{device.id}",
            json=payload,
        )
        return resp


class Feed:
    rel = "/api/feeds"

    def __init__(self, requests):
        self.requests = requests

    def list(self):
        return self.requests.get(self.rel)

    def create(self, feed: FeedModel):
        payload = FeedSchema().dump(feed)
        return self.requests.post(self.rel, json=payload)

    def get(self, feed: FeedModel):
        return self.requests.get(self.rel + f"/{feed.id}")

    def update(self, feed: FeedModel):
        payload = FeedSchema().dump(feed)
        return self.requests.put(self.rel + f"/{feed.id}", json=payload)


class Game:
    rel = "/api/games"

    def __init__(self, requests):
        self.requests = requests

    def get(self, game: GameModel):
        return self.requests.get(self.rel + f"/{game.id}")

    def download(self, game):
        return self.requests.get(self.rel + f"/{game.id}/download")
