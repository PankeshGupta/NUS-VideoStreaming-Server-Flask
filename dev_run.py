#!/usr/bin/env python

from server import app

if __name__ == '__main__':
    # Setting use_reloader=False prevents the app from starting twice in debug mode.
    # This is needed for Redis.

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False, threaded=True)