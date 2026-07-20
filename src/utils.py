import sys
from loguru import logger


def setup_logger(level: str = "INFO") -> None:

    logger.remove()
    logger.add(
        sys.stdout,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> — {message}"
        ),
        level=level,
        colorize=True,
    )
    logger.add(
        "logs/extraction_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG",
        encoding="utf-8",
    )


def sanitize_string(value: str | None, max_len: int = 1000) -> str | None:
    # remove espaços extras
    if value is None:
        return None
    return value.strip()[:max_len]