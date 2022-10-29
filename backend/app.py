import logging

from fastapi import FastAPI
import uvicorn

import routers
from settings import settings


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


if __name__ == '__main__':
    uvicorn.run(app=app, port=9100)
