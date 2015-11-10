DB_URI = 'mysql://team03_15:jTevjFfpZdTYTTy@localhost:3306/team03_15_db?charset=utf8'

# Ensures that all nodes use the same cache server when clustering
USE_CACHE_FOR_POLLING = True

# Use either 'SIMPLE' or 'MEMCACHED'
CACHE_BACKEND = 'MEMCACHED'

# Memcached
MEMCACHED_HOST_PORT = 'localhost:11211'

# Redis --- unused
REDIS_PORT = '8009'

# Gearman
GEARMAND_HOST_PORT = 'localhost:4730'


# Directory for uploaded segment files
DIR_SEGMENT_UPLOADED = 'test_videos/upload'

# Directory for transcoded files
DIR_SEGMENT_TRANSCODED = 'test_videos/sm'

# Base URL for videos file
BASE_URL_VIDEOS = "/videos/sm"

SUPER_USERS = {
    "tony": "whoami",
}
