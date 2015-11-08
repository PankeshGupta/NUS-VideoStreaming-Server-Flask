DB_URI = 'mysql://lpthanh:p@ssw0rd@localhost:3306/flasktest?charset=utf8'

# Ensures that all nodes use the same memcached server when clustering
USE_CACHE_FOR_POLLING = True
MEMCACHED_SERVER = 'localhost:11211'

SUPER_USERS = {
    "tony": "whoami",
}
