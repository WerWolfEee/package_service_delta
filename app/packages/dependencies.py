import uuid
from fastapi import Request, Response


async def get_session(request: Request, response: Response):
    if not request.cookies.get('package_service_cookie'):
        session_id = str(uuid.uuid4())
        response.set_cookie('package_service_cookie', session_id)
        return session_id
    return request.cookies.get('package_service_cookie')
