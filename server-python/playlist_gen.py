#!/usr/bin/env python

import jinja2

templateLoader = jinja2.FileSystemLoader(searchpath="templates_playlist")
templateEnv = jinja2.Environment(loader=templateLoader,
                                 trim_blocks=True,
                                 lstrip_blocks=True,
                                 keep_trailing_newline=False)

template_mpd = templateEnv.get_template("tpl_mpd.jinja2.xml")
template_m3u8_root = templateEnv.get_template("tpl_m3u8_root.jinja2.m3u8")
template_m3u8_stream = templateEnv.get_template("tpl_m3u8_stream.jinja2.m3u8")


def gen_mpd(video_base_url, segment_duration_millis, segment_list, repr_list):
    return template_mpd.render(video_base_url=video_base_url,
                               repr_list=repr_list,
                               segment_duration_millis=segment_duration_millis,
                               segment_list=segment_list)


def gen_m3u8_root(video_base_url, repr_list):
    return template_m3u8_root.render(video_base_url=video_base_url,
                                     repr_list=repr_list)


def gen_m3u8_stream(segment_duration_seconds, segment_list):
    return template_m3u8_stream.render(segment_duration_seconds=segment_duration_seconds,
                                       segment_list=segment_list)


if __name__ == "__main__":
    from models import VideoSegment
    from models import DefaultRepresentations as Reprs

    # test the above method

    base_video_url = "http://www.video.org/myvideo.mp4"
    segment_duration_millis = 3000
    repr_list = [Reprs.HIGH, Reprs.MEDIUM, Reprs.LOW]
    segment_list = []

    segment = VideoSegment()
    segment.uri_mpd = "000001.mp4"
    segment.uri_m3u8 = "000001.ts"
    segment_list.append(segment)

    segment = VideoSegment()
    segment.uri_mpd = "000002.mp4"
    segment.uri_m3u8 = "000002.ts"
    segment_list.append(segment)

    segment = VideoSegment()
    segment.uri_mpd = "000003.mp4"
    segment.uri_m3u8 = "000003.ts"
    segment_list.append(segment)

    print gen_mpd(base_video_url, segment_duration_millis, segment_list, repr_list)
    # print gen_m3u8_root(base_video_url, repr_list)
    # print gen_m3u8_stream(segment_duration_millis / 1000, segment_list)
