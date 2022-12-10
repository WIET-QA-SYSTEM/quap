import logging

from fastapi import FastAPI

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

import uvicorn
from redis import asyncio as aioredis

from settings import settings
import routers


logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"standard": {"format": "%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s"}},
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            }
        },
        "loggers": {"quap": {"handlers": ["console"], "level": "INFO", "propagate": False}},
    }
)
logger = logging.getLogger('quap')


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION
)

app.include_router(routers.data_router)
app.include_router(routers.state_router)
app.include_router(routers.ml_router)


@app.on_event('startup')
async def startup():
    redis = aioredis.from_url(
        f'redis://{settings.REDIS_HOST}',
        port=int(settings.REDIS_PORT),
        encoding='utf8',
        decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')


if __name__ == '__main__':
    uvicorn.run(app=app, port=9100)
