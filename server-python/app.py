#!/usr/bin/env python

from flask import Flask
from flask.ext.restful import Api

app = Flask(__name__)
api = Api(app)

from resources import VideoListResource
from resources import VideoResource
from resources import UploadWavAPI

api.add_resource(VideoListResource, '/videos', endpoint='videos')
api.add_resource(VideoResource, '/videos/<string:id>', endpoint='video')
api.add_resource(UploadWavAPI, '/upload', endpoint='upload')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
