import logging
import logging.config

LOGGING = {
    "version": 1,
    "formatters": {
        "standard": {
            "format": "%(levelname)s:    %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": "app.log",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "myapp": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}

def setup_logging():
    logging.config.dictConfig(LOGGING)