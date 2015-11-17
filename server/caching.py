import logging
import sys

from werkzeug.contrib.cache import MemcachedCache
from werkzeug.contrib.cache import SimpleCache

from settings import CACHE_BACKEND
from settings import MEMCACHED_HOST_PORT

logger = logging.getLogger(__name__)

cache = SimpleCache()

# Provides a simple layer of caching for the video list, based on Memcached.

if "MEMCACHED" == CACHE_BACKEND:
    # Try to use memcached
    try:
        cache = MemcachedCache([MEMCACHED_HOST_PORT])

        # testing the connection
        dummy_data = "The quick brown fox jumps over the lazy dog abcxyz"
        cache.set("cs2015_dummy_data", dummy_data)

        if dummy_data == cache.get("cs2015_dummy_data"):
            logger.info("MemcachedCache was started successfully.")
        else:
            logger.info("MemcachedCache is not working correctly. Using SimpleCache.")
            cache = SimpleCache()

    except RuntimeError as e:
        logger.warn("Error connecting to Memcached. Using SimpleCache. Error=[%r]." % e)

    except:
        logger.warn("Error connecting to Memcached. Error=[%r]." % sys.exc_info()[0])

'''
elif "REDIS" == CACHE_BACKEND:
    # Try to use redis
    try:
        cache = RedisCache(redis)

        # testing the connection
        dummy_data = "The quick brown fox jumps over the lazy dog abcxyz"
        cache.set("cs2015_dummy_data", dummy_data)

        if dummy_data == cache.get("cs2015_dummy_data"):
            logger.info("RedisCache was started successfully.")
        else:
            logger.info("RedisCache is not working correctly. Using SimpleCache.")
            cache = SimpleCache()

    except RuntimeError as e:
        logger.warn("Error connecting to Redis. Using SimpleCache. Error=[%r]." % e)

    except:
        logger.warn("Error connecting to Redis. Error=[%r]." % sys.exc_info()[0])
'''
