from redis import Redis
from rq import Queue
from app.core.settings import settings

# Connect to Redis
redis_conn = Redis(host=settings.redis.host, port=settings.redis.port)

# Create queue
queue = Queue(connection=redis_conn)