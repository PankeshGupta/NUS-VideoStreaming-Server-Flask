import logging
import os
import traceback
from datetime import datetime

from flask import request
from flask.ext.restful import Resource
from flask.ext.restful import abort
from flask.ext.restful import fields
from flask.ext.restful import marshal_with
from flask.ext.restful import reqparse
from gearman import GearmanClient
from sqlalchemy import desc
from werkzeug.datastructures import FileStorage

from admin_auth import auth
from db import session
from models import Video
from models import VideoListCache
from models import VideoSegment
from settings import DIR_SEGMENT_TRANSCODED
from settings import DIR_SEGMENT_UPLOADED
from settings import GEARMAND_HOST_PORT
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
}

video_segment_fields = {
    'segment_id': fields.Integer,
    'video_id': fields.Integer,
    'repr_1_status': fields.String,
    'repr_2_status': fields.String,
    'repr_3_status': fields.String,
    'uri_mpd': fields.String,
    'uri_m3u8': fields.String,
}

# request parser for video
video_parser = reqparse.RequestParser()
video_parser.add_argument('title', type=str)

# request parser for segment (including upload)
segment_parser = reqparse.RequestParser()
segment_parser.add_argument('video_id', type=long)
segment_parser.add_argument('segment_id', type=long)
segment_parser.add_argument('data', type=FileStorage, location='files')

# ensure the directory exists
if not os.path.exists(DIR_SEGMENT_UPLOADED):
    os.makedirs(DIR_SEGMENT_UPLOADED)

if not os.path.exists(DIR_SEGMENT_TRANSCODED):
    os.makedirs(DIR_SEGMENT_TRANSCODED)

# gearman job queue
gm_client = GearmanClient([GEARMAND_HOST_PORT])


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

        session.delete(video)
        session.commit()
        logger.info("Deleted video [%s]" % video_id)

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
        session.add(video)
        session.commit()
        logger.info("Updated video [%s]" % video_id)

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

        session.add(new_video)
        session.commit()

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

    @marshal_with(video_segment_fields)
    def post(self):
        parse_args = segment_parser.parse_args()

        segment = VideoSegment()
        segment.video_id = parse_args['video_id']
        segment.segment_id = parse_args['segment_id']

        # check the video ID
        if not self._fast_check_video_id(segment.video_id):
            abort(404, message="Video (%s) doesn't exist" % segment.video_id)
            return

        segment.uri_mpd = None
        segment.uri_m3u8 = None

        segment.original_extention = parse_args["original_extention"]
        segment.original_path = "%s/%s/%s.%s" % (
            DIR_SEGMENT_UPLOADED,
            segment.video_id,
            segment.segment_id,
            segment.segment_id
        )

        upload_success = True

        try:
            parse_args['data'].save(segment.original_path)
            segment.repr_1_status = 'PROCESSING'
            segment.repr_2_status = 'PROCESSING'
            segment.repr_3_status = 'PROCESSING'

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
            # clean up the uploaded file
            if os.path.exists(segment.original_path):
                os.remove(segment.original_path)

            raise

        if upload_success:
            self._enqueue_segment_task(segment)

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

    @staticmethod
    def _enqueue_segment_task(segment):
        # do this in the background so we don't block the request
        gm_client.submit_job('cs2015_team03_segmentation', segment, background=True)


class VideoSegmentListResource(Resource):
    @marshal_with(video_segment_fields)
    def get(self, video_id):
        segments = session \
            .query(VideoSegment) \
            .filter(VideoSegment.video_id == video_id) \
            .all()
        return segments
