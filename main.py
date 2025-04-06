import asyncio
import uvicorn
from app.database import engine
from app.database import Base


PORT = 8010
HOST = '0.0.0.0'

if __name__ == '__main__':
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_models())

    uvicorn.run(
        app='main:app',
        host=HOST,
        port=PORT,
        reload=True,
        log_config='etc/logging.conf',
    )