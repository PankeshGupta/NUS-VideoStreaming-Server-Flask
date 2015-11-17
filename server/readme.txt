0. Install the Python dependencies
===========================================
Create a virtual environment if needed.

cd server
pip install -r requirements.txt


1. Create database schema
===========================================
cd server_python
python models.py


2. Build the static files for the admin UI
===========================================
2.1. First, install webpack:

npm install webpack -g

2.2. Then build bundle.js by running the build script

cd server/static
npm install
npm run-script build

2.3. To start a daemon that watch the JavaScript files
under app/js and automatically perform a rebuild of
bundle.js, run:

npm run-script watch


3. Install the transcoding utilities
===========================================
Download and install Bento4 from: https://www.bento4.com
Copy the Bento4 binaries files to /usr/local/bin.
Make sure ffmpeg and ffprobe can be found at /usr/local/bin.


3. Start the app
===========================================
Make sure the following processes are started:

memcached
gearmand

Start these in separate terminals:

(the Gearman worker for segment transcoding --- can start multiple processes of this for more parallelism)
server/segment_processor.py

(the main REST API and Admin UI; for deploying on WSGI, look at team03.wsgi instead)
./dev_run.py


4. Description
===========================================
The backend for our system is based on Flask and Flask-Restful, with transcoding pipeline
structured based on Gearman job queue.

With this, the transcoding process is decoupled from the main REST API, so that it be managed
and allocated resources independently from the main app. There can be multiple instances of the transcoder,
but since transcoding is CPU-bound, one needs to make sure that the number of concurrent transcoding processes
are suitable for the number of CPU cores, to reduce context switching costs.

We have a Admin UI built with React.JS and Backbone.JS, to view the uploaded video in real time.
It can be accessed at: http://localhost:5000/
Admin username and password can be found in settings.py (SUPER_USERS).
