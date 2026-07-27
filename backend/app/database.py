import os

from app.settings import DEFAULT_CLICKHOUSE_URL


_ch = None  # ClickHouseLogAdapter singleton; set by init_db()
_logger = None  # AppLogger singleton; set by init_logger() after init_db()


def init_db() -> None:
    """Instantiate and store the ClickHouse adapter singletons."""
    global _ch
    from app.db.clickhouse import ClickHouseLogAdapter
    _ch = ClickHouseLogAdapter(os.getenv("CLICKHOUSE_URL", DEFAULT_CLICKHOUSE_URL))


def init_logger() -> None:
    """Wrap the ClickHouse adapter in AppLogger and store the singleton.

    Must be called after ``init_db()`` so that ``get_ch()`` is available.
    All startup and route code that writes lifecycle events calls ``get_logger()``
    rather than touching ``get_ch()`` directly.
    """
    global _logger
    from app.logger import AppLogger
    _logger = AppLogger(get_ch())  # AppLogger wraps _ch; CH must already be initialised


def get_ch():
    """Return the ClickHouseLogAdapter singleton, raising RuntimeError if not yet initialised."""
    if _ch is None:
        raise RuntimeError("Database not initialised")
    return _ch


def get_logger():
    """Return the AppLogger singleton, raising RuntimeError if not yet initialised."""
    if _logger is None:
        raise RuntimeError("Logger not initialised — call init_logger() after init_db()")  # guards mis-ordered startup
    return _logger
