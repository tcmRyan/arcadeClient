from requests import Session, Response

from client import session
from client.models import AuthModel


class ArcRequest:
    def __init__(self, auth: AuthModel):
        self.session = Session()
        self.auth = auth

    def request(self, method: str, url: str, **kwargs):
        url = self.auth.base_url + url
        method = method.upper()
        headers = kwargs.get("headers", {})
        if self.auth.access_token is not None:
            auth_header = {"Authorization": f"Bearer {self.auth.access_token}"}
            headers.update(auth_header)
        request_args = {"url": url, "method": method}
        kwargs["headers"] = headers
        request_args.update(kwargs)
        print(request_args)
        return self.session.request(**request_args)

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self.request("PUT", url, **kwargs)

    def refresh_token(self, resp: Response):
        if resp.status_code == 401:
            auth_header = {"Authorization": f"Bearer {self.auth.refresh_token}"}
            self.auth.access_token = None
            refresh_resp = self.get("/refresh", headers=auth_header)
            if refresh_resp.status_code == 200:
                self.auth.access_token = refresh_resp.json()["access_token"]
                self.auth.refresh_token = refresh_resp.json(["refresh_token"])
                session.add(self.auth)
                session.commit()
                auth_header = {"Authorization": f"Bearer {self.auth.access_token}"}
                resp.headers = (
                    auth_header
                    if resp.request.headers is None
                    else resp.request.headers.update(auth_header)
                )
                return self.session.send(resp.request)
            else:
                return resp
