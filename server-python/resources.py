from datetime import datetime

from flask.ext.restful import reqparse
from flask.ext.restful import abort
from flask.ext.restful import Resource
from flask.ext.restful import fields
from flask.ext.restful import marshal_with

from werkzeug.datastructures import FileStorage

from models import Video
from db import session

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

    def delete(self, id):
        video = session.query(Video).filter(Video.video_id == id).first()
        if not video:
            abort(404, message="Video {} doesn't exist".format(id))
        session.delete(video)
        session.commit()
        return {}, 204

    @marshal_with(video_fields)
    def put(self, id):
        parsed_args = parser.parse_args()
        video = session.query(Video).filter(Video.video_id == id).first()
        video.title = parsed_args['title']
        session.add(video)
        session.commit()
        return video, 201


class VideoListResource(Resource):
    @marshal_with(video_fields)
    def get(self):
        videos = session.query(Video).all()
        return videos

    @marshal_with(video_fields)
    def post(self):
        parse_args = parser.parse_args()

        new_video = Video()
        new_video.title = parse_args['title']
        new_video.type = 'LIVE'
        new_video.status = 'EMPTY'
        new_video.created_at = datetime.now()

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
