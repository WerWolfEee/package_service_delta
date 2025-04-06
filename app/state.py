import asyncio
from typing import (
    Optional,
)

from app import redis


class State(object):
    def __init__(self, loop: asyncio.BaseEventLoop | asyncio.AbstractEventLoop):
        super().__init__()
        self.loop: asyncio.BaseEventLoop = loop
        self.redis_pool: Optional[redis.Connection] = None
