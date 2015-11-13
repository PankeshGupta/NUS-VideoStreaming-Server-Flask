#!/usr/bin/python
import logging
import os

import sys

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, os.path.abspath("/var/www/cs5248"))

from server import app as application

application.secret_key = 'who knows this?'
