import os
import sqlite3
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from supabase import Client, create_client

BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", BASE_DIR / "data" / "gramconnect.db"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS residents (
  id TEXT PRIMARY KEY, full_name TEXT NOT NULL, phone_hint TEXT NOT NULL,
  locality TEXT NOT NULL, preferred_language TEXT NOT NULL DEFAULT 'Telugu',
  notification_channels TEXT NOT NULL DEFAULT '[]', consent_recorded INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS complaints (
  id TEXT PRIMARY KEY, reference_id TEXT UNIQUE NOT NULL, resident_id TEXT,
  category TEXT NOT NULL, description TEXT NOT NULL, locality TEXT NOT NULL,
  landmark TEXT, priority TEXT NOT NULL, status TEXT NOT NULL, department TEXT,
  authority_reference TEXT, submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(resident_id) REFERENCES residents(id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS complaint_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, complaint_id TEXT NOT NULL, actor_name TEXT NOT NULL,
  event_type TEXT NOT NULL, event_detail TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS outage_alerts (
  id TEXT PRIMARY KEY, reference_id TEXT UNIQUE NOT NULL, locality TEXT NOT NULL,
  source TEXT NOT NULL, details TEXT NOT NULL, status TEXT NOT NULL,
  restoration_estimate TEXT, verified_at TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS notification_deliveries (
  id TEXT PRIMARY KEY, outage_alert_id TEXT NOT NULL, resident_id TEXT NOT NULL,
  channel TEXT NOT NULL, delivery_status TEXT NOT NULL DEFAULT 'Queued', provider_message_id TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(outage_alert_id) REFERENCES outage_alerts(id) ON DELETE CASCADE,
  FOREIGN KEY(resident_id) REFERENCES residents(id) ON DELETE CASCADE
);
"""

def initialise_database() -> None:
    if using_supabase():
        return
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.executescript(SCHEMA)

@contextmanager
def connection():
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def as_dict(row: sqlite3.Row | None):
    return dict(row) if row else None

def using_supabase() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SECRET_KEY)

@lru_cache
def supabase_client() -> Client:
    if not using_supabase():
        raise RuntimeError("Supabase is not configured")
    return create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
