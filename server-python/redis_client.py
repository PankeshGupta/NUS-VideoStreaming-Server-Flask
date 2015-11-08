from redislite import Redis
from redislite import patch

from settings import REDIS_PORT

patch.patch_redis()

redis = Redis(serverconfig={'port': REDIS_PORT})
