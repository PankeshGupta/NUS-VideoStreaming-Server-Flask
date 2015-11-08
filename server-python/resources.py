import logging
from datetime import datetime
from flask import request
from flask.ext.restful import Resource
from flask.ext.restful import abort
from flask.ext.restful import fields
from flask.ext.restful import marshal_with
from flask.ext.restful import reqparse
from sqlalchemy import desc
from werkzeug.datastructures import FileStorage
from models import VideoListCache
from admin_auth import auth
from db import session
from video_repr import DefaultRepresentations as Reprs
from models import Video
from models import VideoSegment
from settings import USE_CACHE_FOR_POLLING

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

video_parser = reqparse.RequestParser()
video_parser.add_argument('title', type=str)


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

        if videos:
            logger.debug("Serving the video list from cache")
        else:
            videos = session \
                .query(Video) \
                .order_by(desc(Video.created_at)) \
                .all()

            if USE_CACHE_FOR_POLLING:
                VideoListCache.set(videos)

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


class VideoSegmentListResource(Resource):
    @marshal_with(video_fields)
    def get(self, video_id):
        segments = session \
            .query(VideoSegment) \
            .filter(VideoSegment.video_id == video_id) \
            .all()
        return segments


class UploadWavAPI(Resource):
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('video_id', type=long)
        parse.add_argument('video', type=FileStorage, location='files')
        args = parse.parse_args()

        args['video'].save("/Users/lpthanh/%s.jpg" % args["id"])
