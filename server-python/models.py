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
from sqlalchemy.orm import composite

from video_repr import VideoRepresentation

Base = declarative_base()


class Video(Base):
    __tablename__ = 'cs_videos'

    video_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now, index=True)

    type = Column(Enum('VOD', 'LIVE', name='cs_video_types'), nullable=False, default='LIVE')
    status = Column(Enum('EMPTY', 'OK', 'ERROR', name='cs_video_status_types'), nullable=False, default='EMPTY')

    segment_count = Column(Integer, nullable=False, default=0)
    segment_duration = Column(Integer, nullable=False, default=3000)

    # if a representation is not available, set its properties to null
    repr_1_name = Column(String(255), nullable=True)
    repr_1_bandwidth = Column(Integer, nullable=True)
    repr_1_width = Column(Integer, nullable=True)
    repr_1_height = Column(Integer, nullable=True)
    repr_1 = composite(VideoRepresentation, repr_1_name, repr_1_bandwidth, repr_1_width, repr_1_height)

    repr_2_name = Column(String(255), nullable=True)
    repr_2_bandwidth = Column(Integer, nullable=True)
    repr_2_width = Column(Integer, nullable=True)
    repr_2_height = Column(Integer, nullable=True)
    repr_2 = composite(VideoRepresentation, repr_2_name, repr_2_bandwidth, repr_2_width, repr_2_height)

    repr_3_name = Column(String(255), nullable=True)
    repr_3_bandwidth = Column(Integer, nullable=True)
    repr_3_width = Column(Integer, nullable=True)
    repr_3_height = Column(Integer, nullable=True)
    repr_3 = composite(VideoRepresentation, repr_3_name, repr_3_bandwidth, repr_3_width, repr_3_height)

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


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from settings import DB_URI

    engine = create_engine(DB_URI)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
