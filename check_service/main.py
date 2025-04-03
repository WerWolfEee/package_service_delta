import aiohttp
import asyncio
import datetime
from decimal import Decimal
import json
import logging
from typing import Optional
from redis.asyncio import Redis
from redis.asyncio.client import PubSub
from app.packages.dao import PackagesDAO
from app.packages.schemas import SPackageCheck
from app import redis
from check_service.schemas import RedisConfig
import  app.redis as app_redis


logger = logging.getLogger(__name__)


class Service:
    def __init__(
            self,
            conf: RedisConfig,
            loop: asyncio.BaseEventLoop,
            redis: Redis
    ):
        super().__init__()
        self.conf: Optional[RedisConfig] = conf
        self.loop: Optional[asyncio.BaseEventLoop] = loop
        self.redis: Optional[Redis] = redis

        self.task: Optional[asyncio.Task] = None

        self.redis_listener: Optional[asyncio.Task] = None
        self.pubsub: Optional[PubSub] = None
        self.queue_name: str = 'start_sync'  # TODO


    async def init(self):
        self.task = self.loop.create_task(self.synchronization_task())

        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe(self.queue_name)
        self.redis_listener = self.loop.create_task(self.listen_redis_task()) # TODO

    async def listen_redis_task(self):
        logger.info("Start redis listener task")
        async for mes in self.pubsub.listen():
            try:
                logger.info(mes)
                if mes['data'] == 1:
                    continue
                if mes['data'] == 'true':
                    res = await PackagesDAO.find_with_no_price()
                    models = []
                    for i in res:
                        models.append(SPackageCheck.model_validate(i))
                    for i in models:
                        price = await self.count_price(i)
                        filter_by = {'id': i.id}
                        values = {'price': price}
                        await PackagesDAO.update(filter_by=filter_by, **values)

            except (KeyboardInterrupt, GeneratorExit, asyncio.CancelledError):
                break
            except Exception as e:
                logger.exception(e)


    @staticmethod
    async def calculate_exchange_value_ttl():
        now = datetime.datetime.now()
        next_day = datetime.datetime(now.year, now.month, now.day + 1, hour=0, minute=0, second=0)
        return datetime.timedelta(next_day.timestamp() - now.timestamp()).seconds

    async def get_dollar_exchange_rate(self) -> float:
        exchange_rate = await app_redis.get(self.redis, 'todays_exchange_rate')
        if exchange_rate is None:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://www.cbr-xml-daily.ru/daily_json.js') as response:  # TODO
                    all_rates = json.loads(await response.text())
                    rate = all_rates.get("Valute").get("USD").get("Value")
                    ttl = await self.calculate_exchange_value_ttl()
                    await app_redis.set(self.redis, 'todays_exchange_rate', rate, ex=ttl)
            return rate
        return exchange_rate


    async def count_price(self, package: SPackageCheck):
        # Стоимость = (вес в кг * 0.5 + стоимость содержимого в долларах * 0.01 ) * курс доллара к рублю
        exchange_rate = await self.get_dollar_exchange_rate()
        res = Decimal(
            (
                    Decimal(package.weight / 1000 * 0.5) +
                    (package.cost_of_contents * Decimal(0.01))
            )
            * Decimal(exchange_rate)
        ).quantize(Decimal("1.00"))
        return  res

    async def synchronization_task(self):
        logger.info("Service started")
        while 1:
            try:
                res = await PackagesDAO.find_with_no_price()
                models = []
                for i in res:
                    models.append(SPackageCheck.model_validate(i))
                for i in models:
                    price = await self.count_price(i)
                    filter_by = {'id': i.id}
                    values = {'price': price}
                    await PackagesDAO.update(filter_by=filter_by, **values)

                await asyncio.sleep(300)  # TODO config

            except (KeyboardInterrupt, GeneratorExit, asyncio.CancelledError):
                logger.info("Service stopping")
                return
            except Exception as e:
                logger.exception(f"Error in check_service: {e}")
                logger.exception(f"{e.__traceback__}")
                await asyncio.sleep(300)


async def run(loop: asyncio.BaseEventLoop):
    config = RedisConfig(dsn='redis://redis')  # TODO
    redis_pool = await redis.init(config)
    service = Service(
        conf=config,
        loop=loop,
        redis=redis_pool
    )
    await service.init()
    return service