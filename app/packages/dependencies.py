import uuid
from fastapi import Request, Response
from app import redis


async def get_session(request: Request, response: Response):
    if not request.cookies.get('package_service_cookie'):
        session_id = str(uuid.uuid4())
        response.set_cookie('package_service_cookie', session_id)
        return session_id
    return request.cookies.get('package_service_cookie')


async def get_redis(request: Request) -> redis.Connection:
    try:
        pool = request.app.state.redis_pool
    except AttributeError:
        raise RuntimeError('Application state has no redis pool')
    else:
        async with await pool as conn:
            yield conn
