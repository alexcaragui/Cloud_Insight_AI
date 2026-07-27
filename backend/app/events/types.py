class LogLevel:  # severity constants used as the ``level`` field in every log write
    INFO = "INFO"   # routine informational entry; operation completed normally
    WARN = "WARN"   # unexpected but non-fatal condition; something may need attention
    ERROR = "ERROR" # operation failed; an exception or error state occurred
    SUCCESS = "SUCCESS" # operation completed successfully; used for lifecycle events
