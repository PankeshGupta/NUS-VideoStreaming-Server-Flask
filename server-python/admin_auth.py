from flask_httpauth import HTTPDigestAuth

auth = None

if auth is None:
    auth = HTTPDigestAuth()
