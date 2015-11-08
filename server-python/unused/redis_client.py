from redislite import Redis
from redislite import patch

from settings import REDIS_PORT

# Original intention was to use Redis for caching and task queue.
# But I found out that the server has both memcached and gearman installed,
# so this is no longer needed, as it will require installing another server.

# Also, since each process importing this file will try to launch its own
# instance of Redis on the same local port, this will be a problem once worker
# processes are started.

patch.patch_redis()

redis = Redis(serverconfig={'port': REDIS_PORT})
