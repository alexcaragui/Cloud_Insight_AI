from app.schemas.logs import ApiLogEntry, AppLogEntry, ChatLogEntry

_api_cols = ", ".join(ApiLogEntry.col_names())
CH_INSERT_API_LOGS = f"INSERT INTO api_logs ({_api_cols}) VALUES"

_app_cols = ", ".join(AppLogEntry.col_names())
CH_INSERT_APP_LOGS = f"INSERT INTO app_logs ({_app_cols}) VALUES"

_chat_cols = ", ".join(ChatLogEntry.col_names())
CH_INSERT_CHAT_LOGS = f"INSERT INTO chat_logs ({_chat_cols}) VALUES"
