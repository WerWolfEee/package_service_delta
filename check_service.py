import asyncio
import logging

from check_service.main import run

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Starting Check Orders service")
    logger.warning("Starting Check Orders service")
    print("Starting Check Orders service")
    loop = asyncio.get_event_loop()     #TODO deprecation

    try:
        loop.run_until_complete(run(loop=loop))
        loop.run_forever()
    except Exception as exc:
        logging.exception(exc)
