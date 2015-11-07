1. Create database schema
===========================================
cd server_python
python models.py

2. Build the static files for the admin UI
===========================================
2.1. First, install webpack:

npm install webpack -g

2.2. Then build bundle.js by running the build script

cd server_python/static
npm install
npm run-script build

2.3. To start a daemon that watch the JavaScript files
under app/js and automatically perform a rebuild of
bundle.js, run:

npm run-script watch