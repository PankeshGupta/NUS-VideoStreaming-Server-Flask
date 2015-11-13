#!/usr/bin/env python

import logging
import multiprocessing as mp
import os
import traceback

from gearman import GearmanWorker
from sqlalchemy.orm import scoped_session

import video_util
from db import session_factory
from models import Video, VideoSegment
from playlist import output_mpd_to_file, output_m3u8_stream_to_files, output_m3u8_root_to_file
from settings import DIR_SEGMENT_TRANSCODED
from settings import GEARMAND_HOST_PORT
from settings import SEGMENT_TASK_NAME

# make sure the output dir exists
if not os.path.exists(DIR_SEGMENT_TRANSCODED):
    os.makedirs(DIR_SEGMENT_TRANSCODED)

#################
# ORM session
#################

session = scoped_session(session_factory)

#################
# Serialization
#################

try:
    import cPickle as pickle
except:
    import pickle

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
# Paths
#################

root_dir = os.path.dirname(os.path.abspath(__file__))
transcode_path = os.path.join(root_dir, DIR_SEGMENT_TRANSCODED)


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


def transcode_segment_for_repr(arg_tuple):
    segment, repr = arg_tuple
    src = segment.original_path

    repr_output_mpd = "%s/%s/%s/%s" % (
        transcode_path,
        segment.video_id,
        repr.name,
        segment.media_mpd
    )

    repr_output_m3u8 = "%s/%s/%s/%s" % (
        transcode_path,
        segment.video_id,
        repr.name,
        segment.media_m3u8
    )

    if repr is None:
        return None

    success = None
    try:
        # for MPD
        logger.info("Encoding segment [%s, %s] for MPD, quality %s, from: %s" %
                    (segment.video_id,
                     segment.segment_id,
                     repr.name,
                     src))

        success = video_util.encode_x264_repr(src, repr_output_mpd, repr)

        # for M3U8
        if success is True:
            # only encode ts if the last one succeeds
            logger.info("Encoding segment [%s, %s] for M3U8, quality %s, from: %s" %
                        (segment.video_id,
                         segment.segment_id,
                         repr.name,
                         src))

            success = video_util.encode_mp42ts(repr_output_mpd, repr_output_m3u8)

    except:
        logger.error("Failed to encoding segment [%s, %s]: %s" %
                     (segment.video_id,
                      segment.segment_id,
                      traceback.format_exc()))

        success = False

    return success


def transcode_segment(video_id, segment_id):
    logger.info("Processing segment %s of video %s" % (segment_id, video_id))

    video = find_video(video_id=video_id)
    if video is None:
        return False

    segment = find_segment(video_id=video_id, segment_id=segment_id)
    if segment is None:
        return False

    if not os.path.exists(segment.original_path):
        logger.error("Segment file does not exist: %s" % segment.original_path)
        return False

    # update status to processing temporarily
    segment.status = 'PROCESSING'
    segment.repr_1_status = 'PROCESSING'
    segment.repr_2_status = 'PROCESSING'
    segment.repr_3_status = 'PROCESSING'

    # update the duration
    segment.duration = video_util.get_duration_millis(segment.original_path)

    try:
        session.add(segment)
        session.commit()
    except:
        session.rollback()
        logger.error("Error saving video segment to database [%s, %s]: %s" %
                     (segment.video_id,
                      segment.segment_id,
                      traceback.format_exc()))
        return False

    segment.media_mpd = "%06d.mp4" % segment.segment_id
    segment.media_m3u8 = "%06d.ts" % segment.segment_id

    repr_list = [video.repr_1, video.repr_2, video.repr_3]

    try:
        # running all transcoding tasks for this segment in parallel
        mp_pool = mp.Pool(processes=len(repr_list))
        task_params = [(segment, r) for r in repr_list]
        task_success = mp_pool.map(transcode_segment_for_repr, task_params)
        mp_pool.close()
        mp_pool.join()

    except:
        logger.error("Error processing video segment [%s, %s]: %s" % (
            segment.video_id, segment.segment_id,
            traceback.format_exc()))

        task_success = [False, False, False]

    # process the results
    task_statuses = map(lambda s: 'NIL' if s is None else 'OK' if s is True else 'ERROR', task_success)
    segment.repr_1_status = task_statuses[0]
    segment.repr_2_status = task_statuses[1]
    segment.repr_3_status = task_statuses[2]

    # the status is only OK if no repr had error
    segment.status = 'OK'
    for task_status in task_statuses:
        if task_status == 'ERROR':
            segment.status = 'ERROR'
            break

    video = find_video(video_id=video_id)
    if video is None:
        # video has been deleted while the encoding was going on
        # clean up the files
        logger.info("Video [%s] has been deleted during the transcoding" % segment.video_id)
        # todo enqueue a task to clean up the files
        return False

    try:
        session.add(segment)
        session.commit()
        logger.info("Finished processing video segment [%s, %s]" % (segment.video_id, segment.segment_id))

    except:
        session.rollback()
        logger.error("Error saving video segment to database [%s, %s]: %s" %
                     (segment.video_id,
                      segment.segment_id,
                      traceback.format_exc()))

        return False

    # update the playlist file
    try:
        output_mpd_to_file(video=video,
                           file_path="%s/%s/%s.mpd" % (transcode_path, segment.video_id, segment.video_id),
                           base_url="")

        output_m3u8_stream_to_files(video=video,
                                    file_paths=
                                    ["%s/%s/%s/stream.m3u8" % (transcode_path, segment.video_id, repr.name)
                                     for repr in repr_list])

        output_m3u8_root_to_file(base_url="",
                                 repr_list=repr_list,
                                 file_path="%s/%s/root.m3u8" % (transcode_path, segment.video_id))

    except:
        logger.error("Error updating play list file [%s, %s]: %s" %
                     (segment.video_id,
                      segment.segment_id,
                      traceback.format_exc()))

        return False

    return True


def generate_thumbnail(video_id, segment_id):
    segment = find_segment(video_id=video_id, segment_id=segment_id)
    if segment is None:
        return False

    if not os.path.exists(segment.original_path):
        logger.error("Segment file does not exist: %s" % segment.original_path)
        return False

    src = segment.original_path
    dst = "%s/%s/thumbnail.jpeg" % (
        transcode_path,
        segment.video_id
    )

    try:
        # for MPD
        if not video_util.gen_thumbnail(src, dst):
            logger.error("Generating thumbnail for segment [%s, %s] from: %s" %
                         (segment.video_id,
                          segment.segment_id,
                          src))

            return False

        # updating the thumbnail info for video
        video = find_video(video_id=video_id)
        if video is None:
            # video has been deleted while the encoding was going on
            # clean up the files
            logger.info("Video [%s] has been deleted" % segment.video_id)
            return False

        video.uri_thumbnail = 'thumbnail.jpeg'

        try:
            session.add(video)
            session.commit()
            logger.info("Generated thumbnail for segment [%s, %s] from: %s" %
                        (segment.video_id,
                         segment.segment_id,
                         src))

            return True

        except:
            session.rollback()
            logger.error("Error saving video to database after generating thumbnail [%s, %s]: %s" %
                         (segment.video_id,
                          segment.segment_id,
                          traceback.format_exc()))

            return False

    except:
        logger.error("Failed to generating thumbnail for segment [%s, %s]: %s" %
                     (segment.video_id,
                      segment.segment_id,
                      traceback.format_exc()))

        return False


def task_listener(gearman_worker, gearman_job):
    task_name, video_id, segment_id = pickle.loads(gearman_job.data)
    result = False

    if task_name == 'transcode':
        result = transcode_segment(video_id, segment_id)
    elif task_name == 'thumbnail':
        result = generate_thumbnail(video_id, segment_id)

    return pickle.dumps(result)


if __name__ == "__main__":
    # worker run

    logger.info("Setting up the worker.")
    gm_worker = GearmanWorker([GEARMAND_HOST_PORT])
    gm_worker.register_task(SEGMENT_TASK_NAME, task_listener)

    try:
        logger.info("Worker was set up successfully. Waiting for work.")
        gm_worker.work()

    except KeyboardInterrupt:
        gm_worker.shutdown()
        logger.info("Worker has shut down successfully. Bye.")
