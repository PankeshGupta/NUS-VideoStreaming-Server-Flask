DB_URI = 'mysql://lpthanh:p@ssw0rd@localhost:3306/flasktest?charset=utf8'

# Ensures that all nodes use the same cache server when clustering
USE_CACHE_FOR_POLLING = True

# Use either 'SIMPLE', or 'MEMCACHED'
CACHE_BACKEND = 'MEMCACHED'

# Memcached
MEMCACHED_HOST_PORT = 'localhost:11211'

SUPER_USERS = {
    "tony": "whoami",
}
