from ksuid import Ksuid
from sqlalchemy import Column, String, DateTime, ColumnElement, Text, Table, ForeignKey, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

from utils.misc import get_timestamp, get_ksuid
from utils.sqlalchemy import BaseExtended

Base = declarative_base()


class AlbumModel(Base, BaseExtended):
    __tablename__ = "albums"
    id = Column(String(length=27), primary_key=True, default=get_ksuid)
    created_at: ColumnElement = Column(DateTime(), default=get_timestamp)
    updated_at: ColumnElement = Column(DateTime(), index=True, default=get_timestamp)
    name = Column(Text(), index=True, unique=True)
    thumbnail_path = Column(String())
    thumbnail_media_id = Column(String(length=27), index=True)
    media = relationship("MediaModel", secondary="media_albums", back_populates="albums")


class MediaModel(Base, BaseExtended):
    __tablename__ = "media"
    id = Column(String(length=27), primary_key=True, default=str(Ksuid()))
    created_at: ColumnElement = Column(DateTime(), default=get_timestamp)
    created_at_ksuid = Column(String(length=27), index=True, default=get_ksuid, unique=True)
    thumbnail_path = Column(String())
    duration = Column(Integer(), index=True)
    webpage_url = Column(String())
    albums = relationship("AlbumModel", secondary="media_albums", back_populates="media")


association_table = Table(
    "media_albums",
    Base.metadata,
    Column("media_id", String(length=36), ForeignKey("media.id"), primary_key=True),
    Column("album_id", String(length=36), ForeignKey("albums.id"), primary_key=True),
)
