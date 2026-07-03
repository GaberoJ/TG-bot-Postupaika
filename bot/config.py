import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "")
YANDEX_PROJECT_ID = os.getenv("YANDEX_PROJECT_ID", "b1gblc7ca9fb1rj110cf")
YANDEX_AGENT_ID = os.getenv("YANDEX_AGENT_ID", "fvto5ko9l2ckfuadm2k2")

# Database
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "project_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "123")
