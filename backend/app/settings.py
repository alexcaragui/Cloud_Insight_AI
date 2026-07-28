
import os


DEFAULT_CLICKHOUSE_URL = os.getenv("CLICKHOUSE_URL", "clickhouse://core-ch:core-ch@clickhouse:9000/core")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODULE_REGISTRY_URLS = os.getenv("MODULE_REGISTRY_URLS", "").split(",")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
