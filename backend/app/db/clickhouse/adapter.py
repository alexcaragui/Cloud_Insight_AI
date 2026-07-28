from datetime import datetime, timezone
import clickhouse_connect

from app.queries.ch_ddl import CH_DDL_API_LOGS, CH_DDL_APP_LOGS, CH_DDL_CHAT_LOGS
from app.queries.ch_selects import (
    CH_TEST_CONNECTION,
    CH_PAGINATED_COUNT, CH_PAGINATED_ROWS,
    CH_SUMMARY_COUNT, CH_SUMMARY_ROWS,
    CH_API_LOGS_SUMMARY, CH_APP_LOGS_SUMMARY,
)
from app.schemas.logs import ApiLogEntry, AppLogEntry, ChatLogEntry
from app.db.clickhouse.utils import _month_start

# SELECT column lists — event_time is added here because it's DB-generated (not in the model)
_API_SELECT_COLS = "event_time, " + ", ".join(ApiLogEntry.col_names())
_API_RESULT_KEYS = ["event_time"] + ApiLogEntry.col_names()

_APP_SELECT_COLS = "event_time, " + ", ".join(AppLogEntry.col_names())
_APP_RESULT_KEYS = ["event_time"] + AppLogEntry.col_names()


class ClickHouseLogAdapter:
    """Manages the 2 fixed ClickHouse log tables and all query operations."""

    def __init__(self, db_url: str) -> None:
        self._client = clickhouse_connect.get_client(dsn=db_url)

    def test_connection(self) -> None:
        self._client.command(CH_TEST_CONNECTION)

    # ------------------------------------------------------------------
    # Migration — run once at startup before DDL provisioning
    # ------------------------------------------------------------------

    def run_migrations(self) -> None:
        """Rename legacy tables, drop old MVs, and normalise column names."""

    # ------------------------------------------------------------------
    # DDL provisioning
    # ------------------------------------------------------------------

    def ensure_api_logs(self) -> None:
        self._client.command(CH_DDL_API_LOGS)

    def ensure_app_logs(self) -> None:
        self._client.command(CH_DDL_APP_LOGS)

    def ensure_chat_logs(self) -> None:
        self._client.command(CH_DDL_CHAT_LOGS)

    # ------------------------------------------------------------------
    # Shared query helpers
    # ------------------------------------------------------------------

    def _paginated_query(
        self,
        table: str,
        select_cols: str,
        from_dt,
        to_dt,
        extra_filters: list,
        extra_params: dict,
        limit: int,
        offset: int,
        order_col: str = "event_time",
        time_col: str = "event_time",
    ):
        from_dt = from_dt or _month_start()
        to_dt = to_dt or datetime.now(timezone.utc)
        where_parts = [
            f"{time_col} >= {{from_dt:DateTime64(3)}}",
            f"{time_col} <= {{to_dt:DateTime64(3)}}",
        ] + extra_filters
        params = {"from_dt": from_dt, "to_dt": to_dt, **extra_params}
        where = "WHERE " + " AND ".join(where_parts)
        total = self._client.query(
            CH_PAGINATED_COUNT.format(table=table, where=where), parameters=params
        ).result_rows[0][0]
        params["limit"] = limit
        params["offset"] = offset
        rows = self._client.query(
            CH_PAGINATED_ROWS.format(select_cols=select_cols, table=table, where=where, order_col=order_col),
            parameters=params,
        ).result_rows
        return rows, total

    def _summary_query(
        self,
        table: str,
        extra_filters: list,
        extra_params: dict,
        from_dt,
        to_dt,
        limit: int,
        offset: int,
    ) -> dict:
        from_dt = from_dt or _month_start()
        to_dt = to_dt or datetime.now(timezone.utc)
        where_parts = [
            "event_time >= {from_dt:DateTime64(3)}",
            "event_time <= {to_dt:DateTime64(3)}",
        ] + extra_filters
        params = {"from_dt": from_dt, "to_dt": to_dt, "limit": limit, "offset": offset, **extra_params}
        where = "WHERE " + " AND ".join(where_parts)
        total = self._client.query(
            CH_SUMMARY_COUNT.format(table=table, where=where), parameters=params
        ).result_rows[0][0]
        rows = self._client.query(
            CH_SUMMARY_ROWS.format(table=table, where=where), parameters=params
        ).result_rows
        keys = ["bucket", "event_type", "event_count", "unique_users"]
        return {"items": [dict(zip(keys, r)) for r in rows], "total": total}

    # ------------------------------------------------------------------
    # API (HTTP request) logs
    # ------------------------------------------------------------------

    def write_api_log(self, entry: ApiLogEntry) -> None:
        self._client.insert(
            "api_logs",
            [list(entry.model_dump().values())],
            column_names=ApiLogEntry.col_names(),
        )

    def query_api_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        event_type: str | None = None,
        owner: str | None = None,
        level: str | None = None,
        from_dt: datetime | None = None,
        to_dt: datetime | None = None,
    ) -> dict:
        extra_filters: list = []
        extra_params: dict = {}
        if event_type:
            extra_filters.append("event_type = {event_type:String}")
            extra_params["event_type"] = event_type
        if owner:
            extra_filters.append("path LIKE {owner:String}")
            extra_params["owner"] = f"%{owner}%"
        if level:
            extra_filters.append("level = {level:String}")
            extra_params["level"] = level
        rows, total = self._paginated_query(
            "api_logs", _API_SELECT_COLS,
            from_dt, to_dt, extra_filters, extra_params, limit, offset,
        )
        return {"items": [dict(zip(_API_RESULT_KEYS, r)) for r in rows], "total": total}

    def query_api_logs_summary(
        self,
        from_dt: datetime | None = None,
        to_dt: datetime | None = None,
        event_type: str | None = None,
        path: str | None = None,
        limit: int = 500,
        offset: int = 0,
    ) -> dict:
        from_dt = from_dt or _month_start()
        to_dt = to_dt or datetime.now(timezone.utc)
        extra_filters: list = []
        extra_params: dict = {}
        if event_type:
            extra_filters.append("event_type = {event_type:String}")
            extra_params["event_type"] = event_type
        if path:
            extra_filters.append("path = {path:String}")
            extra_params["path"] = path
        where_parts = [
            "event_time >= {from_dt:DateTime64(3)}",
            "event_time <= {to_dt:DateTime64(3)}",
        ] + extra_filters
        params = {"from_dt": from_dt, "to_dt": to_dt, "limit": limit, "offset": offset, **extra_params}
        where = "WHERE " + " AND ".join(where_parts)
        rows = self._client.query(CH_API_LOGS_SUMMARY.format(where=where), parameters=params).result_rows
        keys = ["bucket", "event_type", "path", "status_code",
                "request_count", "avg_duration_ms", "max_duration_ms", "error_count"]
        return {"items": [dict(zip(keys, r)) for r in rows], "total": len(rows)}

    # ------------------------------------------------------------------
    # App (platform) logs
    # ------------------------------------------------------------------

    def write_app_log(self, entry: AppLogEntry) -> None:
        self._client.insert(
            "app_logs",
            [list(entry.model_dump().values())],
            column_names=AppLogEntry.col_names(),
        )

    def write_chat_log(self, entry: ChatLogEntry) -> None:
        self._client.insert(
            "chat_logs",
            [list(entry.model_dump().values())],
            column_names=ChatLogEntry.col_names(),
        )

    def query_app_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        event_type: str | None = None,
        caller: str | None = None,
        level: str | None = None,
        from_dt: datetime | None = None,
        to_dt: datetime | None = None,
    ) -> dict:
        extra_filters: list = []
        extra_params: dict = {}
        if event_type:
            extra_filters.append("event_type = {event_type:String}")
            extra_params["event_type"] = event_type
        if caller:
            extra_filters.append("caller = {caller:String}")
            extra_params["caller"] = caller
        if level:
            extra_filters.append("level = {level:String}")
            extra_params["level"] = level
        rows, total = self._paginated_query(
            "app_logs", _APP_SELECT_COLS,
            from_dt, to_dt, extra_filters, extra_params, limit, offset,
        )
        return {"items": [dict(zip(_APP_RESULT_KEYS, r)) for r in rows], "total": total}

    def query_app_logs_summary(
        self,
        from_dt: datetime | None = None,
        to_dt: datetime | None = None,
        event_type: str | None = None,
        caller: str | None = None,
        limit: int = 500,
        offset: int = 0,
    ) -> dict:
        from_dt = from_dt or _month_start()
        to_dt = to_dt or datetime.now(timezone.utc)
        extra_filters: list = []
        extra_params: dict = {}
        if event_type:
            extra_filters.append("event_type = {event_type:String}")
            extra_params["event_type"] = event_type
        if caller:
            extra_filters.append("caller = {caller:String}")
            extra_params["caller"] = caller
        where_parts = [
            "event_time >= {from_dt:DateTime64(3)}",
            "event_time <= {to_dt:DateTime64(3)}",
        ] + extra_filters
        params = {"from_dt": from_dt, "to_dt": to_dt, "limit": limit, "offset": offset, **extra_params}
        where = "WHERE " + " AND ".join(where_parts)
        rows = self._client.query(CH_APP_LOGS_SUMMARY.format(where=where), parameters=params).result_rows
        keys = ["bucket", "event_type", "caller", "event_count"]
        return {"items": [dict(zip(keys, r)) for r in rows], "total": len(rows)}

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def optimize_tables(self, _module_scopes: list[str] = []) -> dict:
        tables = ["api_logs", "app_logs"]
        purged: list[str] = []
        errors: list[str] = []
        for table in tables:
            try:
                self._client.command(f"OPTIMIZE TABLE {table} FINAL")
                purged.append(table)
            except Exception as exc:
                errors.append(f"{table}: {exc}")
        return {"purged": purged, "errors": errors}
