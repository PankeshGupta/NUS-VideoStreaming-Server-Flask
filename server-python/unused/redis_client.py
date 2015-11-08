from redislite import Redis
from redislite import patch

from settings import REDIS_PORT

# Original intention was to use Redis for caching and task queue.
# But I found out that the server has both memcached and gearman installed,
# so this is no longer needed, as it will require installing another server.

patch.patch_redis()

redis = Redis(serverconfig={'port': REDIS_PORT})
