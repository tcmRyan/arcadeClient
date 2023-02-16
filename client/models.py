from typing import List

from sqlalchemy import String, Boolean, Integer, Table, Column, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, backref


class Base(DeclarativeBase):
    pass


feed_games = Table(
    "feed_games",
    Base.metadata,
    Column("feed_id", Integer(), ForeignKey("feed.id"), primary_key=True),
    Column("game_id", Integer(), ForeignKey("game.id"), primary_key=True),
)


class GameModel(Base):
    __tablename__ = "game"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(90))
    path: Mapped[str] = mapped_column(String(180))
    version: Mapped[str] = mapped_column(String(30))
    game_uri: Mapped[str] = mapped_column(String)


class DeviceModel(Base):
    __tablename__ = "device"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(180))
    active: Mapped[bool] = mapped_column(Boolean)
    feed_id: Mapped[int] = mapped_column(Integer, ForeignKey("feed.id"), nullable=True)
    feed: Mapped["FeedModel"] = relationship("FeedModel")
    mac: Mapped[str] = mapped_column(String(30))


class FeedModel(Base):
    __tablename__ = "feed"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(90))
    games: Mapped[List["GameModel"]] = relationship(
        "GameModel",
        secondary=feed_games,
        lazy="subquery",
        backref=backref("feeds", lazy="dynamic"),
    )
    description: Mapped[str] = mapped_column(String(180))
    owner_id: Mapped[int] = mapped_column(Integer)


class AuthModel(Base):
    __tablename__ = "auth"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)
    base_url: Mapped[str] = mapped_column(String)
    access_token: Mapped[str] = mapped_column(String, nullable=True)
    refresh_token: Mapped[str] = mapped_column(String, nullable=True)
    tenant_id: Mapped[int] = mapped_column(String, nullable=True)
