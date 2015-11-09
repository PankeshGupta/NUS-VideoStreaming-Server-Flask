#!/usr/bin/env python

import logging
import multiprocessing as mp
import os
import traceback

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


def transcode_segment_for_repr(segment, repr):
    src = segment.original_path

    repr_output_mpd = "%s/%s/%s/%s" % (
        DIR_SEGMENT_TRANSCODED,
        segment.video_id,
        repr.name,
        segment.media_mpd
    )

    repr_output_m3u8 = "%s/%s/%s/%s" % (
        DIR_SEGMENT_TRANSCODED,
        segment.video_id,
        repr.name,
        segment.media_m3u8
    )

    if repr is None:
        return None

    success = None
    try:
        # for MPD
        logger.info("Encoding segment [%s, %s] for MPD, from: %s" % (segment.video_id, segment.segment_id, src))
        success = transcoding.encode_x264_repr(src, repr_output_mpd, repr)

        # for M3U8
        if success is True:
            # only encode ts if the last one succeeds
            logger.info("Encoding segment [%s, %s] for M3U8, from: %s" % (segment.video_id, segment.segment_id, src))
            success = transcoding.encode_mp42ts(repr_output_mpd, repr_output_m3u8)

    except:
        logger.error(
            "Failed to encoding segment [%s, %s]: %s" % (segment.video_id, segment.segment_id, traceback.format_exc()))
        success = False

    return success


def transcode_segment(video_id, segment_id):
    video = find_video(video_id=video_id)
    if video is None:
        return

    segment = find_segment(video_id=video_id, segment_id=segment_id)
    if segment is None:
        return

    if not os.path.exists(segment.original_path):
        logger.error("Segment file does not exist: %s", segment.original_path)
        return

    segment.media_mpd = "%s.mp4" % segment.segment_id
    segment.media_m3u8 = "%s.ts" % segment.segment_id

    repr_list = [video.repr_1, video.repr_2, video.repr_3]

    # running all transcoding tasks for this segment in parallel
    mp_pool = mp.Pool(processes=len(repr_list))
    task_success = mp_pool.map(transcode_segment_for_repr, [(segment, r) for r in repr_list])
    mp_pool.close()
    mp_pool.join()

    # process the results
    task_status = map(lambda s: 'NIL' if s is None else 'OK' if s is True else 'ERROR', task_success)
    segment.repr_1_status = task_status[0]
    segment.repr_2_status = task_status[1]
    segment.repr_3_status = task_status[2]

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
