import logging
import os

from flask import Flask
from flask import render_template
from flask import send_from_directory
from flask.ext.restful import Api
from flask_sqlalchemy_session import flask_scoped_session

from db import session_factory
from settings import SUPER_USERS, DIR_SEGMENT_TRANSCODED

app = Flask(__name__, static_url_path='')
flask_scoped_session(session_factory, app)

# authentication for admin resources
app.config['SECRET_KEY'] = 'who knows this?'
from admin_auth import auth

#################
# Ftatic files
#################

root_dir = os.path.dirname(os.path.abspath(__file__))

static_app = os.path.join(root_dir, 'static', 'app')
static_video_files = os.path.join(root_dir, DIR_SEGMENT_TRANSCODED)

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
from resources import VideoEndResource
from resources import LiveMpdResource
from resources import LiveM3U8RootResource
from resources import LiveM3U8StreamResource

api.add_resource(VideoListResource, '/videos', endpoint='video_list')
api.add_resource(VideoResource, '/video/<int:video_id>', endpoint='video')
api.add_resource(VideoEndResource, '/video_end/<int:video_id>', endpoint='video_end')

api.add_resource(VideoSegmentListResource, '/video_segment/<int:video_id>', endpoint='video_segment_list')
api.add_resource(VideoSegmentResource, '/video_segment/<int:video_id>/<int:segment_id>', endpoint='video_segment')

api.add_resource(LiveMpdResource, '/live_mpd/<int:video_id>.mpd', endpoint='live_mpd')
api.add_resource(LiveM3U8RootResource, '/live_m3u8/<int:video_id>/root.m3u8', endpoint='live_m3u8')
api.add_resource(LiveM3U8StreamResource, '/live_m3u8/<int:video_id>/<string:repr_name>/stream.m3u8',
                 endpoint='live_m3u8_stream')


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
    return send_from_directory(static_app, path)


# serves video files
@app.route('/video_files/<path:path>')
def send_video(path):
    return send_from_directory(static_video_files, path)
