CH_DDL_API_LOGS = """
CREATE TABLE IF NOT EXISTS api_logs (
    event_time  DateTime64(3) DEFAULT now64(),
    level       LowCardinality(String) DEFAULT 'INFO',
    event_type  LowCardinality(String),
    path        String DEFAULT '',
    method      LowCardinality(String) DEFAULT '',
    status_code Int16 DEFAULT 0,
    duration_ms Float32 DEFAULT 0,
    message     String DEFAULT '',
    details     String DEFAULT '{}'
) ENGINE = MergeTree()
ORDER BY event_time
TTL toDateTime(event_time) + INTERVAL 30 DAY
"""  # DDL for the HTTP request log table; auto-expires rows after 30 days via TTL

CH_DDL_APP_LOGS = """
CREATE TABLE IF NOT EXISTS app_logs (
    event_time  DateTime64(3) DEFAULT now64(),
    level       LowCardinality(String) DEFAULT 'INFO',
    event_type  LowCardinality(String),
    caller      String DEFAULT '',
    message     String DEFAULT '',
    details     String DEFAULT '{}'
) ENGINE = MergeTree()
ORDER BY event_time
TTL toDateTime(event_time) + INTERVAL 30 DAY
"""  # DDL for the platform lifecycle log table; auto-expires rows after 30 days
