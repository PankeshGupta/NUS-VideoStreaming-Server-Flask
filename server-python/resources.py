import logging
import os
import traceback
from datetime import datetime

from flask import request, make_response
from flask.ext.restful import Resource
from flask.ext.restful import abort
from flask.ext.restful import fields
from flask.ext.restful import marshal_with
from flask.ext.restful import reqparse
from flask_sqlalchemy_session import current_session as session
from gearman import GearmanClient
from sqlalchemy import desc, asc
from werkzeug.datastructures import FileStorage

from admin_auth import auth
from models import Video
from models import VideoListCache
from models import VideoSegment
from playlist import gen_mpd, gen_m3u8_root, gen_m3u8_stream
from settings import DIR_SEGMENT_TRANSCODED, BASE_URL_VIDEOS
from settings import DIR_SEGMENT_UPLOADED
from settings import GEARMAND_HOST_PORT
from settings import SEGMENT_TASK_NAME
from settings import USE_CACHE_FOR_POLLING
from video_repr import DefaultRepresentations as Reprs

logger = logging.getLogger(__name__)

video_fields = {
    'video_id': fields.Integer,
    'title': fields.String,
    'created_at': fields.DateTime,
    'type': fields.String,
    'status': fields.String,

    'segment_count': fields.Integer,
    'segment_duration': fields.Integer,

    'repr_1_name': fields.String,
    'repr_1_bandwidth': fields.Integer,
    'repr_1_width': fields.Integer,
    'repr_1_height': fields.Integer,

    'repr_2_name': fields.String,
    'repr_2_bandwidth': fields.Integer,
    'repr_2_width': fields.Integer,
    'repr_2_height': fields.Integer,

    'repr_3_name': fields.String,
    'repr_3_bandwidth': fields.Integer,
    'repr_3_width': fields.Integer,
    'repr_3_height': fields.Integer,

    'uri_mpd': fields.String,
    'uri_m3u8': fields.String,

    'uri_thumbnail': fields.String,

    'base_url': fields.String,
}

video_segment_fields = {
    'segment_id': fields.Integer,
    'video_id': fields.Integer,
    'original_path': fields.String,
    'original_extension': fields.String,
    'repr_1_status': fields.String,
    'repr_2_status': fields.String,
    'repr_3_status': fields.String,
    'media_mpd': fields.String,
    'media_m3u8': fields.String,
}

# request parser for video
video_parser = reqparse.RequestParser()
video_parser.add_argument('title', type=str)

# request parser for segment (including upload)
segment_parser = reqparse.RequestParser()
segment_parser.add_argument('segment_id', type=long, location='form')
segment_parser.add_argument('original_extension', type=str, location='form')
segment_parser.add_argument('data', type=FileStorage, location='files')

# request parser for the ending request
video_end_parser = reqparse.RequestParser()
video_end_parser.add_argument('last_segment_id', type=long, location='form')

# ensure the directory exists
if not os.path.exists(DIR_SEGMENT_UPLOADED):
    os.makedirs(DIR_SEGMENT_UPLOADED)

if not os.path.exists(DIR_SEGMENT_TRANSCODED):
    os.makedirs(DIR_SEGMENT_TRANSCODED)

# gearman job queue
gm_client = GearmanClient([GEARMAND_HOST_PORT])

# importing pickle
try:
    import cPickle as pickle
except:
    import pickle


class VideoResource(Resource):
    @marshal_with(video_fields)
    def get(self, video_id):
        video = session \
            .query(Video) \
            .filter(Video.video_id == video_id) \
            .first()

        if not video:
            abort(404, message="Video {} doesn't exist".format(video_id))

        return video

    @auth.login_required
    def delete(self, video_id):
        logger.info("Deleting video [%s]" % video_id)

        video = session \
            .query(Video) \
            .filter(Video.video_id == video_id) \
            .first()

        if not video:
            abort(404, message="Video {} doesn't exist".format(video_id))

        try:
            session.delete(video)
            session.commit()
            logger.info("Deleted video [%s]" % video_id)

        except:
            session.rollback()
            logger.error("Error persistent data: %s" % traceback.format_exc())
            raise

        return {}, 204

    @marshal_with(video_fields)
    @auth.login_required
    def put(self, video_id):
        logger.info("Updating video [%s]" % video_id)
        parsed_args = video_parser.parse_args()

        video = session \
            .query(Video) \
            .filter(Video.video_id == video_id) \
            .first()

        video.title = parsed_args['title']

        try:
            session.add(video)
            session.commit()
            logger.info("Updated video [%s]" % video_id)

        except:
            session.rollback()
            logger.error("Error persistent data: %s" % traceback.format_exc())
            raise

        return video, 201


class VideoListResource(Resource):
    @marshal_with(video_fields)
    def get(self):
        videos = None

        if USE_CACHE_FOR_POLLING and request.args.get('_admin', None) == 'yes':
            # serve from cache, since this is mostly polling
            videos = VideoListCache.get()

        if videos is None:
            videos = session \
                .query(Video) \
                .order_by(desc(Video.created_at)) \
                .all()

            if USE_CACHE_FOR_POLLING:
                VideoListCache.set(videos)

        else:
            logger.debug("Serving the video list from cache")

        return videos

    @marshal_with(video_fields)
    def post(self):
        parse_args = video_parser.parse_args()

        new_video = Video()
        new_video.title = parse_args['title']
        new_video.type = 'LIVE'
        new_video.status = 'EMPTY'
        new_video.created_at = datetime.now()
        new_video.segment_count = 0
        new_video.segment_duration = 3000
        new_video.repr_1 = Reprs.HIGH
        new_video.repr_2 = Reprs.MEDIUM
        new_video.repr_3 = Reprs.LOW
        new_video.uri_mpd = None
        new_video.uri_m3u8 = None

        try:
            session.add(new_video)
            session.commit()

        except:
            session.rollback()
            raise

        return new_video, 201


class VideoSegmentResource(Resource):
    @marshal_with(video_segment_fields)
    def get(self, video_id, segment_id):
        segment = session \
            .query(VideoSegment) \
            .filter((VideoSegment.video_id == video_id) & (VideoSegment.segment_id == segment_id)) \
            .first()

        if not segment:
            abort(404, message="Segment (%s, %s) doesn't exist" % (video_id, segment_id))

        return segment


class VideoSegmentListResource(Resource):
    @marshal_with(video_segment_fields)
    def get(self, video_id):
        segments = session \
            .query(VideoSegment) \
            .filter(VideoSegment.video_id == video_id) \
            .all()
        return segments

    @marshal_with(video_segment_fields)
    def post(self, video_id):
        parse_args = segment_parser.parse_args()

        segment = VideoSegment()
        segment.video_id = video_id
        segment.segment_id = parse_args['segment_id']
        segment.status = 'NIL'
        segment.repr_1_status = 'NIL'
        segment.repr_2_status = 'NIL'
        segment.repr_3_status = 'NIL'

        # check the video ID
        video = session \
            .query(Video) \
            .filter(Video.video_id == video_id) \
            .first()

        if not video:
            abort(404, message="Video (%s) doesn't exist" % segment.video_id)
            return

        # update the segment count if needed
        expected_segment_count = segment.segment_id + 1
        if video.segment_count < expected_segment_count:
            video.segment_count = expected_segment_count
            video.status = 'UPLOADING'
            session.add(video)
            session.flush()

        segment.uri_mpd = None
        segment.uri_m3u8 = None

        segment.original_extension = parse_args["original_extension"]
        segment.original_path = "%s/%s/%s.%s" % (
            DIR_SEGMENT_UPLOADED,
            segment.video_id,
            segment.segment_id,
            segment.original_extension
        )

        upload_success = True

        try:
            # processing the uploaded file

            # creating the directory
            dir_path = os.path.dirname(segment.original_path)
            if not os.path.exists(dir_path) \
                    or not os.path.isdir(dir_path):
                os.mkdir(dir_path)

            uploaded_file = parse_args['data']
            uploaded_file.save(dst=segment.original_path, buffer_size=524288)

        except:
            upload_success = False
            logger.error("Error processing segment upload: %r" % traceback.format_exc())
            segment.repr_1_status = 'ERROR'
            segment.repr_2_status = 'ERROR'
            segment.repr_3_status = 'ERROR'

        try:
            session.add(segment)
            session.commit()

        except:
            session.rollback()

            # clean up the uploaded file
            if os.path.exists(segment.original_path):
                os.remove(segment.original_path)

            logger.error("Error persistent data: %s" % traceback.format_exc())
            raise

        if upload_success:
            enqueue_segment_task('transcode', segment.video_id, segment.segment_id)

        return segment, 201

    @staticmethod
    def _fast_check_video_id(video_id):
        has_id = VideoListCache.has_id(video_id)

        if has_id is None or not isinstance(has_id, bool):
            video = session \
                .query(Video) \
                .filter(Video.video_id == video_id) \
                .first()
            return video is not None

        return has_id


class VideoEndResource(Resource):
    @marshal_with(video_fields)
    def post(self, video_id):
        parse_args = video_end_parser.parse_args()

        last_segment_id = parse_args['last_segment_id']
        if not last_segment_id:
            abort(400, message="Expecting last_segment_id")
            return None

        # check the video
        video = session \
            .query(Video) \
            .filter(Video.video_id == video_id) \
            .first()

        if not video:
            abort(404, message="Video (%s) doesn't exist" % video_id)
            return None

        video.segment_count = last_segment_id + 1
        video.type = 'VOD'
        video.status = 'OK'

        # generate the thumbnail
        thumbnail_segment_id = int(video.segment_count / 2)
        enqueue_segment_task('thumbnail', video.video_id, thumbnail_segment_id)

        try:
            session.add(video)
            session.commit()

        except:
            session.rollback()
            logger.error("Error persistent data: %s" % traceback.format_exc())
            raise

        return video


class LiveMpdResource(Resource):
    def get(self, video_id):

        # check the video
        video = session \
            .query(Video) \
            .filter(Video.video_id == video_id) \
            .first()

        if not video:
            abort(404, message="Video (%s) doesn't exist" % video_id)
            return None

        last_obtained_segment = request.args.get('last_segment_id', None)
        response_data = LiveMpdResource.build_mpd_string("%s/%s" % (BASE_URL_VIDEOS, video.video_id),
                                                         video,
                                                         last_obtained_segment)

        response = make_response(response_data)
        response.headers['content-type'] = 'application/dash+xml'
        response.headers['content-disposition'] = 'attachment; filename="%s.mpd"' % video.video_id

        return response

    @staticmethod
    def build_mpd_string(base_url, video, last_obtained_segment=None):
        segments = []
        if last_obtained_segment is not None:
            segments = session \
                .query(VideoSegment) \
                .filter((VideoSegment.video_id == video.video_id) &
                        (VideoSegment.segment_id > last_obtained_segment) &
                        (VideoSegment.status == 'OK')) \
                .order_by(asc(VideoSegment.segment_id)) \
                .all()
        else:
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


class LiveM3U8RootResource(Resource):
    def get(self, video_id):
        # check the video
        video = session \
            .query(Video) \
            .filter(Video.video_id == video_id) \
            .first()

        if not video:
            abort(404, message="Video (%s) doesn't exist" % video_id)
            return None

        response_data = LiveM3U8RootResource.build_root_m3u8_string("", video)

        response = make_response(response_data)
        response.headers['content-type'] = 'application/vnd.apple.mpegurl'
        response.headers['content-disposition'] = 'attachment; filename="%s.m3u8"' % video.video_id

        return response

    @staticmethod
    def build_root_m3u8_string(base_url, video):
        repr_list = [video.repr_1, video.repr_2, video.repr_3]
        return gen_m3u8_root(base_url=base_url,
                             repr_list=repr_list)


class LiveM3U8StreamResource(Resource):
    def get(self, video_id, repr_name):
        # check the video
        video = session \
            .query(Video) \
            .filter(Video.video_id == video_id) \
            .first()

        if not video:
            abort(404, message="Video (%s) doesn't exist" % video_id)
            return None

        response_data = LiveM3U8StreamResource.build_stream_m3u8_string(video,
                                                                        "%s/%s/%s" %
                                                                        (BASE_URL_VIDEOS, video.video_id, repr_name))

        response = make_response(response_data)
        response.headers['content-type'] = 'application/vnd.apple.mpegurl'
        response.headers['content-disposition'] = 'attachment; filename="%s.%s.m3u8"' % (video.video_id, repr_name)

        return response

    @staticmethod
    def build_stream_m3u8_string(video, base_url):
        segments = session \
            .query(VideoSegment) \
            .filter((VideoSegment.video_id == video.video_id) &
                    (VideoSegment.status == 'OK')) \
            .order_by(asc(VideoSegment.segment_id)) \
            .all()

        return gen_m3u8_stream(segment_duration_seconds=video.segment_duration / 1000,
                               segment_list=segments,
                               base_url=base_url)


def enqueue_segment_task(task_name, video_id, segment_id):
    # do this in the background so we don't block the request
    gm_client.submit_job(SEGMENT_TASK_NAME,
                         pickle.dumps((task_name, video_id, segment_id)),
                         background=True)

    logger.info("Submitted task [%s] into queue for segment [%s, %s]" % (task_name, video_id, segment_id))
