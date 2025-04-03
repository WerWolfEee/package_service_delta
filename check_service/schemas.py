from pydantic import BaseModel

class RedisConfig(BaseModel):
    dsn: str
    minsize: int = 1
    maxsize: int = 10
