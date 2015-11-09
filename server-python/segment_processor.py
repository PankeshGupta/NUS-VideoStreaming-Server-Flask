#!/usr/bin/env python

import logging
import os

from gearman import GearmanWorker

import transcoding
from db import session
from models import Video, VideoSegment
from settings import DIR_SEGMENT_TRANSCODED
from settings import GEARMAND_HOST_PORT

# make sure the output dir exists
if not os.path.exists(DIR_SEGMENT_TRANSCODED):
    os.makedirs(DIR_SEGMENT_TRANSCODED)

#################
# Logging
#################

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)

rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)
rootLogger.addHandler(consoleHandler)

logger = logging.getLogger(__name__)


#################
# Init the worker
#################


def find_video(video_id):
    video = session \
        .query(Video) \
        .filter(Video.video_id == video_id) \
        .first()

    if video is None:
        logger.error("Video ID was not found: %s" % video_id)

    return video


def find_segment(video_id, segment_id):
    segment = session \
        .query(VideoSegment) \
        .filter((VideoSegment.video_id == video_id) & (VideoSegment.segment_id == segment_id)) \
        .first()

    if segment is None:
        logger.error("Segment was not found: %s|%s" % (video_id, segment_id))

    return segment


def transcode_segment(segment):
    video = find_video(video_id=segment.video_id)
    if video is None:
        return

    segment = find_segment(video_id=segment.video_id, segment_id=segment.segment_id)
    if segment is None:
        return

    if not os.path.exists(segment.original_path):
        logger.error("Segment file does not exist: %s", segment.original_path)
        return

    src = segment.original_path

    segment.media_mpd = "%s.mp4" % segment.segment_id
    segment.media_m3u8 = "%s.ts" % segment.segment_id

    overall_success = []

    for repr in [video.repr_1, video.repr_2, video.repr_3]:
        repr_output_mpd = "%s/%s/%s/%s" % (
            DIR_SEGMENT_TRANSCODED,
            video.video_id,
            repr.name,
            segment.media_mpd
        )

        repr_output_m3u8 = "%s/%s/%s/%s" % (
            DIR_SEGMENT_TRANSCODED,
            video.video_id,
            repr.name,
            segment.media_m3u8
        )

        success = True
        try:
            # for MPD
            logger.info("Encoding segment [%s, %s] for MPD" % (segment.video_id, segment.segment_id))
            success = transcoding.encode_x264_repr(src, repr_output_mpd, repr)

            # for M3U8
            if success is True:
                # only encode ts if the last one succeeds
                logger.info("Encoding segment [%s, %s] for M3U8" % (segment.video_id, segment.segment_id))
                success = transcoding.encode_mp42ts(repr_output_mpd, repr_output_m3u8)
        except:
            success = False

        overall_success.append(success)

    segment.repr_1_status = 'OK' if overall_success[0] is True else 'ERROR'
    segment.repr_2_status = 'OK' if overall_success[1] is True else 'ERROR'
    segment.repr_3_status = 'OK' if overall_success[2] is True else 'ERROR'

    session.add(segment)
    session.commit()
    logger.info("Finished processing video segment [%s, %s]" % (segment.video_id, segment.segment_id))


def task_listener(gearman_worker, gearman_job):
    segment = gearman_job.data
    transcode_segment(segment)


if __name__ == "__main__":
    # worker run

    logger.info("Setting up the worker.")
    gm_worker = GearmanWorker([GEARMAND_HOST_PORT])
    gm_worker.register_task('cs2015_team03_segmentation', task_listener)

    try:
        logger.info("Worker was set up successfully. Waiting for work.")
        gm_worker.work()

    except KeyboardInterrupt:
        gm_worker.shutdown()
        logger.info("Worker has shut down successfully. Bye.")
