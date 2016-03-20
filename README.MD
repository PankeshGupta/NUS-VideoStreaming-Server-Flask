## Description
This project is part of the Systems Support for Continuous Media module in NUS. The requirement is to create a system for video streaming in two modes: Live Stream and Video-on-Demand (VOD). The project is composed of three components:
* Android app for video recording
* Android app for video playback
* Backend server for uploading, transcoding, and serving videos

The full requirement can be found on the [module's website](http://www.comp.nus.edu.sg/~cs5248/proj.html).

The Android app is hosted [here](https://github.com/tonylpt/nus-videostreaming-android).

## Implementation

### The API
The REST API was built on [Flask](http://flask.pocoo.org) and [Flask-Restful](http://flask-restful-cn.readthedocs.org/en/0.3.4). Video information (metadata, transcoding status, thumbnail, etc.) is stored in MySQL using [SQLAlchemy](http://www.sqlalchemy.org). Video segments are stored on the local file system. For each video segment, a job will be published into Gearman for the transcoder.

### The Transcoder
To enable parallelism for the transcoding process, we used Gearman as a job queue and a set of worker processes to listen for transcoding requests. Each request spawns three processes using Python's [multiprocessing](https://docs.python.org/2/library/multiprocessing.html) to run ffmpeg transcoder for three quality levels (DASH).

With this, the transcoding process is decoupled from the main REST API, so that it be managed and allocated resources independently from the main app. There can be multiple instances of the transcoder, but since transcoding is CPU-bound, one needs to make sure that the number of concurrent transcoding processes are suitable for the number of CPU cores, to reduce context switching costs.

### The Dashboard
![Screenshot](/screenshot-server.jpeg?raw=true "Screenshot")

We added a simple dashboard (in addition to the project requirements) to let the admin view the list of uploaded videos (updated in real-time). Due to the lack of time, the dashboard has only a few feature, such as delete or rename videos. It was built on [ReactJS](https://facebook.github.io/react) with Flux and [BackboneJS](http://backbonejs.org). This was considered an experiment with React rather than a full attempt to implement a comprehensive dashboard.

The dashboard can be accessed at http://localhost:5000. Admin username and password can be found in settings.py (under SUPER_USERS).


## Project Structure
* \_\_init__.py             : app bootstrap
* models.py               : database schema based on SQLAlchemy
* resources.py            : Flask-Restful resources
* settings.py             : config information
* playlist.py             : utility to generate live playlist based on Jinja2 templates
* video_util.py           : utility to transcode a video by wrapping ffmpeg and other tools
* segment_processor.py   : Gearman worker for transcoding and generating thumbnail

## Setup

1. Install the Python dependencies. Create a virtual environment if needed:

```
cd server
pip install -r requirements.txt
```

2. Create database schema:

```
cd server_python
python models.py
```

3. Build the static files for the admin UI

Install webpack:

```
npm install webpack -g
```

Build bundle.js by running the build script:

```
cd server/static
npm install
npm run-script build
```

To start a daemon that watch the JavaScript files
under app/js and automatically perform a rebuild of
bundle.js, run:

```
npm run-script watch
```

4. Install the transcoding utilities:

* Download and install Bento4 from https://www.bento4.com and copy the Bento4 binaries files to /usr/local/bin.

* Make sure ffmpeg and ffprobe can be found at /usr/local/bin.


5. Install memcached and gearmand.


## Run

1. Make sure memcached and gearmand are running.

2. Start the Gearman worker for segment transcoding (start multiple instances of this for more parallelism):

```
server/segment_processor.py
```

3. The main REST API and Admin UI (for deploying on WSGI, look at team03.wsgi instead):

```
./dev_run.py
```

## Team Members
* Tony Luong (lpthanh{at}gmail.com)
* Randy Tandriansyah (randytandriansyah{at}gmail.com)
