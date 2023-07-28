import logging
import sys


class ColoredFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(message)s"  # type: ignore

    FORMATS = {
        logging.DEBUG: grey + format + reset,  # type: ignore
        logging.INFO: grey + format + reset,  # type: ignore
        logging.WARNING: yellow + format + reset,  # type: ignore
        logging.ERROR: red + format + reset,  # type: ignore
        logging.CRITICAL: bold_red + format + reset,  # type: ignore
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger(__name__)

stdout_handler = logging.StreamHandler(stream=sys.stdout)
stdout_handler.setFormatter(ColoredFormatter())

file_handler = logging.FileHandler(f"{__name__}.log")
file_handler.setFormatter(
    logging.Formatter(fmt="[%(asctime)s: %(levelname)s] %(message)s")
)

logger.addHandler(stdout_handler)
logger.addHandler(file_handler)
