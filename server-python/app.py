#!/usr/bin/env python

import logging

from flask import Flask
from flask import render_template
from flask import send_from_directory
from flask.ext.restful import Api

from settings import SUPER_USERS

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'who knows this?'

from admin_auth import auth

#################
# Logging
#################

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)

rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)
rootLogger.addHandler(consoleHandler)

#################
# API
#################

api = Api(app)

from resources import VideoListResource
from resources import VideoResource
from resources import VideoSegmentResource
from resources import VideoSegmentListResource
from resources import UploadWavAPI

api.add_resource(VideoListResource, '/videos', endpoint='videos')
api.add_resource(VideoResource, '/video/<int:id>', endpoint='video')
api.add_resource(VideoSegmentListResource, '/video_segments/<int:video_id>', endpoint='video_segments')
api.add_resource(VideoSegmentResource, '/video_segment/<int:video_id>/<int:segment_id>', endpoint='video_segment')
api.add_resource(UploadWavAPI, '/upload', endpoint='upload')


#################
# Web App
#################

@auth.get_password
def get_password(username):
    if username in SUPER_USERS:
        return SUPER_USERS.get(username)
    return None


@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')


# serves static files during development
@app.route('/app/<path:path>')
def send_js(path):
    print "requesting %s" % path
    return send_from_directory('static/app', path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
