from client.models import DeviceModel, FeedModel


def test_device(session, device, feed):
    device = session.query(DeviceModel).first()
    feed = session.query(FeedModel).first()
    device.current_feed = feed
    session.add(device)
    session.commit()
    assert len(device.feed.games) == 5
