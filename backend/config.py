"""
config.py
All settings, read once from environment (.env in dev). This project uses
SQLite as its one and only database, and Google Gemini as its one and only
LLM provider — no branching, no alternate code paths. (If you ever need
Postgres instead, the only change required is DATABASE_URL + swapping the
SQLite-specific connect_args in database.py — everything else, including
every model and query, is already database-agnostic SQLAlchemy.)
"""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    # --- Database (SQLite only) -------------------------------------------
    DATABASE_URL: str = "sqlite:///./resort.db"
    CHECKPOINT_DB_PATH: str = "./checkpoints.sqlite"

    # --- LLM (Google Gemini only) -------------------------------------------
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "3"))

    # --- Guardrails -----------------------------------------------------------
    MAX_QTY_PER_ITEM: int = int(os.getenv("MAX_QTY_PER_ITEM", "20"))
    MAX_ITEMS_PER_ORDER: int = int(os.getenv("MAX_ITEMS_PER_ORDER", "15"))

    # --- Misc -------------------------------------------------------------------
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    ENV: str = os.getenv("ENV", "development")


settings = Settings()
