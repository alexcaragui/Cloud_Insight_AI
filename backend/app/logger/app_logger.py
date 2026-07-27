import json

from app.db.clickhouse import ClickHouseLogAdapter
from app.events import LogLevel
from app.events.lifecycle import lifecycle_message
from app.schemas.logs import ApiLogEntry, AppLogEntry


class AppLogger:
    """Single entry point for all ClickHouse lifecycle event writes.

    Wraps ClickHouseLogAdapter so callers never touch the adapter directly.
    Every method silently suppresses exceptions — a CH outage must never
    degrade the API.
    """

    def __init__(self, ch: ClickHouseLogAdapter) -> None:
        self._ch = ch

    # ------------------------------------------------------------------
    # App / system events → app_logs table
    # ------------------------------------------------------------------

    def app(
        self,
        event_type: str,
        caller: str,
        *,
        message: str = "",
        details: dict | None = None,
    ) -> None:
        try:
            self._ch.write_app_log(AppLogEntry(
                level=LogLevel.INFO,
                event_type=event_type,
                caller=caller,
                message=message or lifecycle_message(event_type, caller),
                details=json.dumps(details or {}),
            ))
        except Exception:
            pass

    # ------------------------------------------------------------------
    # HTTP request log → api_logs table
    # ------------------------------------------------------------------

    def request(
        self,
        path: str,
        method: str,
        status_code: int,
        duration_ms: float,
        *,
        caller: str = "unknown",
        message: str = "",
        details: dict | None = None,
    ) -> None:
        try:
            self._ch.write_api_log(ApiLogEntry(
                level=LogLevel.INFO,
                event_type="http.request",
                path=path,
                method=method,
                status_code=status_code,
                duration_ms=round(duration_ms, 2),
                message=message,
                details=json.dumps(details or {}),
            ))
        except Exception:
            pass
