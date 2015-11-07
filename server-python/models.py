#!/usr/bin/env python

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class VideoRepresentation(Base):
    __tablename__ = 'cs_representations'

    repr_id = Column(String(100), primary_key=True)
    bandwidth = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)


class Video(Base):
    __tablename__ = 'cs_videos'

    video_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now, index=True)

    type = Column(Enum('VOD', 'LIVE', name='cs_video_types'), nullable=False, default='LIVE')
    status = Column(Enum('EMPTY', 'OK', 'ERROR', name='cs_video_status_types'), nullable=False, default='EMPTY')

    segment_count = Column(Integer, nullable=False, default=0)
    segment_duration = Column(Integer, nullable=False, default=3000)

    # if a representation is not available, set it to null
    repr_1_id = Column(String(100), ForeignKey(VideoRepresentation.repr_id), nullable=True)
    repr_2_id = Column(String(100), ForeignKey(VideoRepresentation.repr_id), nullable=True)
    repr_3_id = Column(String(100), ForeignKey(VideoRepresentation.repr_id), nullable=True)

    # each uri can be a dynamic resource (live streaming) or a static file (on demand)
    uri_mpd = Column(String(255), nullable=True)
    uri_m3u8 = Column(String(255), nullable=True)


class VideoSegment(Base):
    __tablename__ = 'cs_segments'

    video_id = Column(Integer, ForeignKey(Video.video_id), index=True)
    segment_id = Column(Integer, autoincrement=False)

    # segment status for each representation
    repr_1_status = Column(Enum('OK', 'ERROR', 'PROCESSING', 'NIL'), nullable=False, default='NIL')
    repr_2_status = Column(Enum('OK', 'ERROR', 'PROCESSING', 'NIL'), nullable=False, default='NIL')
    repr_3_status = Column(Enum('OK', 'ERROR', 'PROCESSING', 'NIL'), nullable=False, default='NIL')

    # uri for each type of playlist
    uri_mpd = Column(String(255), nullable=True)
    uri_m3u8 = Column(String(255), nullable=True)

    __table_args__ = (PrimaryKeyConstraint(video_id, segment_id, name='cs_segments_pk'), {},)


class DefaultRepresentations(object):
    HIGH = VideoRepresentation()
    HIGH.repr_id = 'HIGH'
    HIGH.bandwidth = 3000000
    HIGH.width = 720
    HIGH.height = 480

    MEDIUM = VideoRepresentation()
    MEDIUM.repr_id = 'MEDIUM'
    MEDIUM.bandwidth = 768000
    MEDIUM.width = 480
    MEDIUM.height = 320

    LOW = VideoRepresentation()
    LOW.repr_id = 'LOW'
    LOW.bandwidth = 200000
    LOW.width = 240
    LOW.height = 160


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from settings import DB_URI

    engine = create_engine(DB_URI)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    from db import session

    # create the default representations
    session.add(DefaultRepresentations.HIGH)
    session.add(DefaultRepresentations.MEDIUM)
    session.add(DefaultRepresentations.LOW)

    session.commit()
