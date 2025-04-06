import json
import logging
from typing import Any, Optional
from check_service.schemas import RedisConfig
from redis.asyncio import from_url, Redis

logger = logging.getLogger(__name__)

Connection = Redis


async def init(config: RedisConfig) -> Connection:
    dsn = config.dsn

    if not dsn:
        raise RuntimeError('Redis connection parameters not defined')

    global Connection
    Connection = await from_url(
        dsn,
        max_connections=config.maxsize
    )
    return Connection


async def close(pool: Connection):
    await pool.aclose()


async def get(conn: Connection, key: str) -> dict | float | None:
    data = await conn.get(key)
    if data is not None:
        try:
            return json.loads(data)
        except:
            logger.exception(f'Wrong session data {data}')
    return None


async def set(conn: Connection, key: str, value: Any, ex: Optional[int] = None):
    await conn.set(key, json.dumps(value), ex=ex)


async def del_(conn: Connection, key: str):
    await conn.delete(key)


async def publish(
        conn: Connection,
        queue_name: str,
        data: Any
):
    await conn.publish(channel=queue_name, message=json.dumps(data))
