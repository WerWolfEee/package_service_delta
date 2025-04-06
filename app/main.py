import asyncio
import logging
from fastapi import FastAPI
from app.packages.router import router as router_packages
from app import redis
from app.state import State
from check_service.schemas import RedisConfig

logger = logging.getLogger(__name__)


def factory():
    loop = asyncio.new_event_loop()

    state = State(
        loop=loop
    )

    app = FastAPI(
        title='Package Delivery Service REST API',
        )

    app.state = state
    app.include_router(router_packages)
    register_startup(app)

    return app


def register_startup(app):
    @app.on_event("startup")
    async def handler_startup():
        logger.info('Startup called')
        try:
            await startup(app)
            logger.info("REST API app startup executed")
        except:
            logger.exception('Startup crashed')



async def startup(app):
    state: State = app.state

    config = RedisConfig(dsn='redis://redis')  # TODO
    state.redis_pool = await redis.init(config)

    return app


app = factory()


@app.get("/")
def home_page():
    return {"message": "Стартовая страница"}
