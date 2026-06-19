import logging
from typing import Optional

try:
    import redis.asyncio as aioredis
except Exception:
    aioredis = None

logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self, url: Optional[str] = None):
        self.url = url
        self.client = None
        self.is_available = False

    async def connect(self):
        if not aioredis or not self.url:
            logger.info("Redis not configured or redis library not installed; skipping Redis connection.")
            self.is_available = False
            return
        try:
            self.client = aioredis.from_url(self.url)
            await self.client.ping()
            self.is_available = True
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            self.is_available = False

    async def ping(self) -> bool:
        if not self.client:
            return False
        try:
            await self.client.ping()
            return True
        except Exception:
            return False

redis_manager = RedisManager()
