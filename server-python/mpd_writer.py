import jinja2

templateLoader = jinja2.FileSystemLoader(searchpath=".")
templateEnv = jinja2.Environment(loader=templateLoader,
                                 trim_blocks=True,
                                 lstrip_blocks=True,
                                 keep_trailing_newline=False)

template = templateEnv.get_template("mpd_template.xml")


def write_mpd(video_base_url, segment_duration, segment_list, repr_list):
    return template.render(video_base_url=video_base_url,
                           repr_list=repr_list,
                           segment_duration=segment_duration,
                           segment_list=segment_list)


if __name__ == "__main__":
    from models import VideoRepresentation
    from models import VideoSegment

    # test the above method

    base_video_url = "http://www.video.org/myvideo.mp4"
    segment_duration = 3000
    repr_list = []
    segment_list = []

    repr = VideoRepresentation()
    repr.repr_id = 'HIGH'
    repr.bandwidth = 3000000
    repr.width = 720
    repr.height = 480
    repr_list.append(repr)

    repr = VideoRepresentation()
    repr.repr_id = 'MEDIUM'
    repr.bandwidth = 768000
    repr.width = 480
    repr.height = 320
    repr_list.append(repr)

    repr = VideoRepresentation()
    repr.repr_id = 'LOW'
    repr.bandwidth = 200000
    repr.width = 240
    repr.height = 160
    repr_list.append(repr)

    segment = VideoSegment()
    segment.file_name = "000001.mp4"
    segment_list.append(segment)

    segment = VideoSegment()
    segment.file_name = "000002.mp4"
    segment_list.append(segment)

    segment = VideoSegment()
    segment.file_name = "000003.mp4"
    segment_list.append(segment)

    print write_mpd(base_video_url, segment_duration, segment_list, repr_list)
