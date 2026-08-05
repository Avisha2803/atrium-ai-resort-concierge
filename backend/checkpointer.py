"""
checkpointer.py
Opens LangGraph's persistent SQLite checkpointer (conversation memory store)
for the app's lifetime. File-backed, so memory survives restarts.
"""

from contextlib import contextmanager

from langgraph.checkpoint.sqlite import SqliteSaver

from backend.config import settings


@contextmanager
def get_checkpointer():
    with SqliteSaver.from_conn_string(settings.CHECKPOINT_DB_PATH) as saver:
        yield saver
