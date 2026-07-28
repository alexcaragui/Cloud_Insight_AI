from pydantic import BaseModel, Field

class ApiLogEntry(BaseModel):
    level: str
    event_type: str
    path: str
    method: str
    status_code: int
    duration_ms: float
    message: str = ""
    details: str = "{}"       # JSON: {"body": ..., "query": ...}

    @classmethod
    def col_names(cls) -> list[str]:
        return list(cls.model_fields.keys())

class AppLogEntry(BaseModel):
    level: str
    event_type: str
    caller: str               # e.g. "fe", "helpers/process_video"
    message: str
    details: str = "{}"       # JSON

    @classmethod
    def col_names(cls) -> list[str]:
        return list(cls.model_fields.keys())

class ChatLogEntry(BaseModel):
    session_id: str
    model: str
    user_message: str
    assistant_reply: str
    duration_ms: float = 0.0

    @classmethod
    def col_names(cls) -> list[str]:
        return list(cls.model_fields.keys())