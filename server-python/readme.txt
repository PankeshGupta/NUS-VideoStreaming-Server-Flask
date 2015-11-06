1. Create database schema
===========================================
cd server_python
python models.py

2. Build the static files for the admin UI
===========================================
cd server_python/static
npm install
npm run-script build

That will build the bundle.js file for the admin
web app. To have it watch the js files under app/js and
automatically perform rebuild, run:

npm run-script watch