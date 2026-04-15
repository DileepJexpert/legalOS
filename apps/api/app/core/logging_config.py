from __future__ import annotations

import logging
import sys


def setup_logging(debug: bool = True) -> None:
    """Configure root logging for the LegalOS API.

    Call this once at application startup.  All modules then use the
    standard ``logging.getLogger(__name__)`` pattern and inherit this
    configuration automatically.
    """
    level = logging.DEBUG if debug else logging.INFO

    fmt = "%(asctime)s | %(levelname)-8s | %(name)-35s | %(message)s"
    date_fmt = "%H:%M:%S"

    root = logging.getLogger()
    root.setLevel(level)

    # Remove any handlers that uvicorn or a previous call may have installed
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(fmt, datefmt=date_fmt))
    root.addHandler(handler)

    # Suppress noisy third-party loggers so our own logs stay readable
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)
    # uvicorn already prints access lines; we add our own richer middleware
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
