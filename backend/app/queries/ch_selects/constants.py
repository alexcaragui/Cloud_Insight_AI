# {table}, {where}, {select_cols}, {order_col} are str.format() placeholders.
# {{limit:UInt32}} / {{offset:UInt32}} are double-braced so str.format() emits literal
# {limit:UInt32} / {offset:UInt32} — consumed by clickhouse-connect as server-side params.

CH_TEST_CONNECTION = "SELECT 1"  # minimal connectivity probe; raises on unreachable ClickHouse
CH_PAGINATED_COUNT = "SELECT count() FROM {table} {where}"  # total-row count for the pagination metadata field
CH_PAGINATED_ROWS = (
    "SELECT {select_cols} FROM {table} {where}"
    " ORDER BY {order_col} DESC LIMIT {{limit:UInt32}} OFFSET {{offset:UInt32}}"
)
CH_SUMMARY_COUNT = (
    "SELECT count() FROM"
    " (SELECT 1 FROM {table} {where} GROUP BY toStartOfHour(event_time), event_type)"
)
CH_SUMMARY_ROWS = """
SELECT toStartOfHour(event_time) AS bucket, event_type,
       count() AS event_count, uniq(owner) AS unique_users
FROM {table} {where}
GROUP BY bucket, event_type
ORDER BY bucket DESC
LIMIT {{limit:UInt32}} OFFSET {{offset:UInt32}}
"""  # hourly GROUP BY aggregate used by all module and bot summary endpoints

CH_API_LOGS_SUMMARY = """
SELECT toStartOfHour(event_time) AS bucket, event_type, path, status_code,
       count() AS request_count,
       round(avg(duration_ms), 2) AS avg_duration_ms,
       max(duration_ms) AS max_duration_ms,
       countIf(status_code >= 400) AS error_count
FROM api_logs {where}
GROUP BY bucket, event_type, path, status_code
ORDER BY bucket DESC
LIMIT {{limit:UInt32}} OFFSET {{offset:UInt32}}
"""  # richer summary for the API logs UI; includes path, status, latency, and error counts

CH_APP_LOGS_SUMMARY = """
SELECT toStartOfHour(event_time) AS bucket, event_type, caller,
       count() AS event_count
FROM app_logs {where}
GROUP BY bucket, event_type, caller
ORDER BY bucket DESC
LIMIT {{limit:UInt32}} OFFSET {{offset:UInt32}}
"""  # hourly summary for the app logs UI; groups by event type and caller
