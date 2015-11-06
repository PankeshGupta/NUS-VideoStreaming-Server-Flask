#!/usr/bin/env python

from flask import Flask, send_from_directory
from flask_httpauth import HTTPDigestAuth
from flask.ext.restful import Api
from settings import SUPER_USERS

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'who knows this?'
auth = HTTPDigestAuth()

#################
# API
#################

api = Api(app)

from resources import VideoListResource
from resources import VideoResource
from resources import UploadWavAPI

api.add_resource(VideoListResource, '/videos', endpoint='videos')
api.add_resource(VideoResource, '/video/<string:id>', endpoint='video')
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
    return "Hello, %s!" % auth.username()


# serves static files during development
@app.route('/app/<path:path>')
def send_js(path):
    print "requesting %s" % path
    return send_from_directory('static/app', path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
