import logging.config
from pathlib import Path

from dotenv import load_dotenv


ENV_PATH = Path(__file__).parent.parent / '.env'

load_dotenv(ENV_PATH)


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

logger = logging.getLogger("quap")
