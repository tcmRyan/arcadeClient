from client import db
from client.models import DeviceModel, FeedModel


def test_device(session, device, feed):
    device = db.session.query(DeviceModel).first()
    feed = db.session.query(FeedModel).first()
    device.feed = feed
    db.session.add(device)
    db.session.commit()
    assert len(device.feed.games) == 5
