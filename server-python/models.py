#!/usr/bin/env python

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Video(Base):
    __tablename__ = 'cs_videos'

    video_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    type = Column(Enum('VOD', 'LIVE', name='cs_video_types'), nullable=False, default='LIVE')
    status = Column(Enum('EMPTY', 'OK', 'ERROR', name='cs_video_status_types'), nullable=False, default='EMPTY')


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from settings import DB_URI

    engine = create_engine(DB_URI)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
