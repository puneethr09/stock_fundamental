import sqlite3
import json
from typing import Dict, Any, List, Optional
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "research.db"


def _ensure_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS assignments (
            assignment_id TEXT PRIMARY KEY,
            payload TEXT NOT NULL
        )
    """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id TEXT,
            user_id TEXT,
            payload TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            badge_type TEXT,
            payload TEXT,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS progress_metrics (
            user_id TEXT PRIMARY KEY,
            payload TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            type TEXT,
            payload TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()


def save_assignment(assignment: Dict[str, Any]) -> None:
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO assignments (assignment_id, payload) VALUES (?, ?)",
        (assignment["assignment_id"], json.dumps(assignment)),
    )
    conn.commit()
    conn.close()


def get_assignment(assignment_id: str) -> Optional[Dict[str, Any]]:
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT payload FROM assignments WHERE assignment_id = ?", (assignment_id,)
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return json.loads(row[0])


def save_completion(assignment_id: str, user_id: str, payload: Dict[str, Any]) -> None:
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO completions (assignment_id, user_id, payload) VALUES (?, ?, ?)",
        (assignment_id, user_id, json.dumps(payload)),
    )
    conn.commit()
    conn.close()


def get_completions_for_user(user_id: str) -> List[Dict[str, Any]]:
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT assignment_id, payload, created_at FROM completions WHERE user_id = ?",
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    out = []
    for aid, payload, created_at in rows:
        out.append(
            {
                "assignment_id": aid,
                "payload": json.loads(payload),
                "created_at": created_at,
            }
        )
    return out


def save_badge(user_id: str, badge: Dict[str, Any]) -> None:
    """Persist an awarded badge for a user."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO badges (user_id, badge_type, payload) VALUES (?, ?, ?)",
        (user_id, badge.get("badge_type"), json.dumps(badge)),
    )
    conn.commit()
    conn.close()


def get_badges_for_user(user_id: str) -> List[Dict[str, Any]]:
    """Return list of persisted badges for a user."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT badge_type, payload, earned_at FROM badges WHERE user_id = ? ORDER BY earned_at DESC",
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    out = []
    for badge_type, payload, earned_at in rows:
        try:
            payload_obj = json.loads(payload)
        except Exception:
            payload_obj = {}
        out.append(
            {"badge_type": badge_type, "payload": payload_obj, "earned_at": earned_at}
        )
    return out


def save_notification(user_id: str, ntype: str, payload: Dict[str, Any]) -> None:
    """Persist a notification for a user."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO notifications (user_id, type, payload) VALUES (?, ?, ?)",
        (user_id, ntype, json.dumps(payload)),
    )
    conn.commit()
    conn.close()


def get_notifications_for_user(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Return recent notifications for a user."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT type, payload, created_at FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    out = []
    for ntype, payload, created_at in rows:
        try:
            payload_obj = json.loads(payload)
        except Exception:
            payload_obj = {}
        out.append({"type": ntype, "payload": payload_obj, "created_at": created_at})
    return out


def save_progress_metrics(user_id: str, progress: Dict[str, Any]) -> None:
    """Persist progress metrics for a user (upsert)."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO progress_metrics (user_id, payload, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
        (user_id, json.dumps(progress)),
    )
    conn.commit()
    conn.close()


def get_progress_metrics(user_id: str) -> Optional[Dict[str, Any]]:
    """Get persisted progress metrics for a user."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT payload FROM progress_metrics WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    try:
        return json.loads(row[0])
    except Exception:
        return None
