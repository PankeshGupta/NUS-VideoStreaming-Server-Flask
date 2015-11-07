import logging
from datetime import datetime

from flask.ext.restful import Resource
from flask.ext.restful import abort
from flask.ext.restful import fields
from flask.ext.restful import marshal_with
from flask.ext.restful import reqparse
from sqlalchemy import desc
from werkzeug.datastructures import FileStorage

from admin_auth import auth
from db import session
from models import DefaultRepresentations as Reprs
from models import Video

logger = logging.getLogger(__name__)

video_fields = {
    'video_id': fields.Integer,
    'title': fields.String,
    'created_at': fields.DateTime,
    'type': fields.String,
    'status': fields.String,
}

parser = reqparse.RequestParser()
parser.add_argument('title', type=str)


class VideoResource(Resource):
    @marshal_with(video_fields)
    def get(self, id):
        video = session.query(Video).filter(Video.video_id == id).first()
        if not video:
            abort(404, message="Video {} doesn't exist".format(id))
        return video

    @auth.login_required
    def delete(self, id):
        logger.info("Deleting video [%s]" % id)
        video = session.query(Video).filter(Video.video_id == id).first()
        if not video:
            abort(404, message="Video {} doesn't exist".format(id))
        session.delete(video)
        session.commit()
        logger.info("Deleted video [%s]" % id)
        return {}, 204

    @marshal_with(video_fields)
    @auth.login_required
    def put(self, id):
        logger.info("Updating video [%s]" % id)
        parsed_args = parser.parse_args()
        video = session.query(Video).filter(Video.video_id == id).first()
        video.title = parsed_args['title']
        session.add(video)
        session.commit()
        logger.info("Updated video [%s]" % id)
        return video, 201


class VideoListResource(Resource):
    @marshal_with(video_fields)
    def get(self):
        videos = session.query(Video).order_by(desc(Video.created_at)).all()
        return videos

    @marshal_with(video_fields)
    def post(self):
        parse_args = parser.parse_args()

        new_video = Video()
        new_video.title = parse_args['title']
        new_video.type = 'LIVE'
        new_video.status = 'EMPTY'
        new_video.created_at = datetime.now()
        new_video.segment_count = 0
        new_video.segment_duration = 3000
        new_video.repr_1_id = Reprs.HIGH.repr_id
        new_video.repr_2_id = Reprs.MEDIUM.repr_id
        new_video.repr_3_id = Reprs.LOW.repr_id

        session.add(new_video)
        session.commit()
        return new_video, 201


class UploadWavAPI(Resource):
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('video_id', type=long)
        parse.add_argument('video', type=FileStorage, location='files')
        args = parse.parse_args()

        args['video'].save("/Users/lpthanh/%s.jpg" % args["id"])
