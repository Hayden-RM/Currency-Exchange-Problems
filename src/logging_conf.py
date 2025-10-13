# src/logging_conf.py
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(
    logfile: str = "logs/debug.log",
    env_var: str = "A1_DEBUG",
    default_level: int = logging.INFO,
) -> Path:
    """
    Configure root logger for console + rotating file, overriding any prior config.
    Returns the absolute path of the logfile.
    """
    level = logging.DEBUG if os.getenv(env_var) else default_level
    log_path = Path(logfile).expanduser().resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=level,
        format="%(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(log_path, mode="w", maxBytes=1_000_000,
                                backupCount=1, encoding="utf-8"),
        ],
        force=True,  # <-- overrides any existing logging config
    )
    logging.getLogger().debug(f"[probe] Logging set to {logging.getLevelName(level)}; file={log_path}")
    return log_path
