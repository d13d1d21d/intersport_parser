import logging
import pathlib
from datetime import datetime as dt


def date_str(date: dt) -> str:
	return date.strftime("%Y-%m-%d")

def init_logger(path: str, format: str, level: int | str) -> logging.Logger:
    pathlib.Path("logs/").mkdir(exist_ok=True) 

    logger = logging.Logger("parser_errors")
    logger.setLevel(level)

    ch_file = logging.FileHandler(path, delay=True, encoding="utf-8")
    ch_file.setLevel(level)
    logger.addHandler(ch_file)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter(format))
    logger.addHandler(ch)

    return logger