from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

DEFAULT_DB_PATH = Path(os.environ.get("LCSRS_DB", "./lcsrs.db")).resolve()

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS problems (
  lc_num      INTEGER PRIMARY KEY,
  title       TEXT    NOT NULL,
  phase       TEXT    NOT NULL,
  plan_order  INTEGER NOT NULL UNIQUE,
  is_optional INTEGER NOT NULL DEFAULT 0,
  note        TEXT,
  created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS reviews (
  lc_num        INTEGER PRIMARY KEY,
  due_at        INTEGER NOT NULL,
  interval_days REAL    NOT NULL,
  ease          REAL    NOT NULL,
  reps          INTEGER NOT NULL,
  lapses        INTEGER NOT NULL,
  easy_streak   INTEGER NOT NULL,
  last_grade    TEXT    NOT NULL,
  status        TEXT    NOT NULL DEFAULT 'active',
  updated_at    INTEGER NOT NULL,
  FOREIGN KEY(lc_num) REFERENCES problems(lc_num) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS review_logs (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  lc_num       INTEGER NOT NULL,
  reviewed_at  INTEGER NOT NULL,
  grade        TEXT    NOT NULL,
  prev_due_at  INTEGER,
  next_due_at  INTEGER,
  prev_intvl   REAL,
  next_intvl   REAL,
  prev_ease    REAL,
  next_ease    REAL,
  note         TEXT,
  FOREIGN KEY(lc_num) REFERENCES problems(lc_num) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_reviews_due ON reviews(due_at);
CREATE INDEX IF NOT EXISTS idx_logs_time  ON review_logs(reviewed_at);
"""

DEFAULT_META = {
    "cursor_plan_order": "1",
    "new_quota": "1",
    "review_per_new": "3",
    "interleave_ratio": "0",  # MVP 先关
    "window_size": "30",
}

def connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@contextmanager
def tx(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    try:
        conn.execute("BEGIN;")
        yield conn
        conn.execute("COMMIT;")
    except Exception:
        conn.execute("ROLLBACK;")
        raise

def init_db(db_path: Path = DEFAULT_DB_PATH) -> Path:
    conn = connect(db_path)
    with tx(conn):
        conn.executescript(SCHEMA_SQL)
        for k, v in DEFAULT_META.items():
            conn.execute(
                "INSERT INTO meta(key,value) VALUES(?,?) "
                "ON CONFLICT(key) DO NOTHING;",
                (k, v),
            )
    conn.close()
    return db_path
