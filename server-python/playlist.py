#!/usr/bin/env python

import logging
import jinja2
from flask_sqlalchemy_session import current_session as session
from sqlalchemy import asc
from db import session_factory
from sqlalchemy.orm import scoped_session
from models import Video, VideoSegment

logger = logging.getLogger(__name__)

#################
# ORM session
#################

session = scoped_session(session_factory)

#################
# Templates
#################

templateLoader = jinja2.FileSystemLoader(searchpath="templates_playlist")
templateEnv = jinja2.Environment(loader=templateLoader,
                                 trim_blocks=True,
                                 lstrip_blocks=True,
                                 keep_trailing_newline=False)

template_mpd = templateEnv.get_template("tpl_mpd.jinja2.xml")
template_m3u8_root = templateEnv.get_template("tpl_m3u8_root.jinja2.m3u8")
template_m3u8_stream = templateEnv.get_template("tpl_m3u8_stream.jinja2.m3u8")


def gen_mpd(base_url, segment_duration_millis, segment_list, repr_list):
    return template_mpd.render(base_url=base_url,
                               repr_list=repr_list,
                               segment_duration_millis=segment_duration_millis,
                               segment_list=segment_list)


def gen_m3u8_root(base_url, repr_list):
    return template_m3u8_root.render(repr_list=repr_list)


def gen_m3u8_stream(segment_duration_seconds, segment_list):
    return template_m3u8_stream.render(segment_duration_seconds=segment_duration_seconds,
                                       segment_list=segment_list)


def output_mpd_to_string(video, base_url):
    segments = session \
        .query(VideoSegment) \
        .filter((VideoSegment.video_id == video.video_id) &
                (VideoSegment.status == 'OK')) \
        .order_by(asc(VideoSegment.segment_id)) \
        .all()

    repr_list = [video.repr_1, video.repr_2, video.repr_3]
    return gen_mpd(base_url=base_url,
                   repr_list=repr_list,
                   segment_duration_millis=video.segment_duration,
                   segment_list=segments)


def output_mpd_to_file(video, file_path, base_url):
    logger.info("Updating playlist file: %s" % file_path)

    with open(file_path, "w") as text_file:
        text_file.write(output_mpd_to_string(video, base_url))


def output_m3u8_stream_to_string(video):
    segments = session \
        .query(VideoSegment) \
        .filter((VideoSegment.video_id == video.video_id) &
                (VideoSegment.status == 'OK')) \
        .order_by(asc(VideoSegment.segment_id)) \
        .all()

    return gen_m3u8_stream(segment_duration_seconds=video.segment_duration / 1000,
                           segment_list=segments)


def output_m3u8_stream_to_files(video, file_paths):
    logger.info("Updating playlist files: %s" % file_paths)

    m3u8_str = output_m3u8_stream_to_string(video)
    for file_path in file_paths:
        with open(file_path, "w") as text_file:
            text_file.write(m3u8_str)


if __name__ == "__main__":
    from models import VideoSegment
    from video_repr import DefaultRepresentations as Reprs

    # test the above method

    base_url = "http://www.video.org/myvideo.mp4"
    segment_duration_millis = 3000
    repr_list = [Reprs.HIGH, Reprs.MEDIUM, Reprs.LOW]
    segment_list = []

    segment = VideoSegment()
    segment.media_mpd = "000001.mp4"
    segment.media_m3u8 = "000001.ts"
    segment_list.append(segment)

    segment = VideoSegment()
    segment.media_mpd = "000002.mp4"
    segment.media_m3u8 = "000002.ts"
    segment_list.append(segment)

    segment = VideoSegment()
    segment.media_mpd = "000003.mp4"
    segment.media_m3u8 = "000003.ts"
    segment_list.append(segment)

    # print gen_mpd(base_url, segment_duration_millis, segment_list, repr_list)
    # print gen_m3u8_root(base_url, repr_list)
    print gen_m3u8_stream(segment_duration_millis / 1000, segment_list)
