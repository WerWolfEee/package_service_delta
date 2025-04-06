import asyncio
import logging

from check_service.main import run

logger = logging.getLogger(__name__)
logger.setLevel(10)


if __name__ == "__main__":
    logger.info("Starting Check Orders service")
    loop = asyncio.new_event_loop()

    try:
        loop.run_until_complete(run(loop=loop))
        loop.run_forever()
    except Exception as exc:
        logging.exception(exc)
