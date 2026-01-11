import sqlite3
from datetime import datetime
from app.models import get_db
def insert_message(msg):
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?)""",
            (
                msg["message_id"],
                msg["from"],
                msg["to"],
                msg["ts"],
                msg.get("text"),
                datetime.utcnow().isoformat() + "Z",
            ),
        )
        conn.commit()
        return "created"
    except sqlite3.IntegrityError:
        return "duplicate"
    finally:
        conn.close()
def list_messages(filters, limit, offset):
    base = "FROM messages WHERE 1=1"
    params = []
    if filters.get("from"):
        base += " AND from_msisdn = ?"
        params.append(filters["from"])

    if filters.get("since"):
        base += " AND ts >= ?"
        params.append(filters["since"])

    if filters.get("q"):
        base += " AND lower(text) LIKE ?"
        params.append(f"%{filters['q'].lower()}%")

    count_q = "SELECT COUNT(*) " + base
    data_q = (
        "SELECT message_id, from_msisdn as 'from', to_msisdn as 'to', ts, text "
        + base +
        " ORDER BY ts ASC, message_id ASC LIMIT ? OFFSET ?"
    )
    conn = get_db()
    total = conn.execute(count_q, params).fetchone()[0]
    rows = conn.execute(data_q, params + [limit, offset]).fetchall()
    conn.close()
    return total, [dict(r) for r in rows]
def stats():
    conn = get_db()
    cur = conn.cursor()
    total = cur.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    senders = cur.execute(
        "SELECT from_msisdn as 'from', COUNT(*) as count FROM messages GROUP BY from_msisdn ORDER BY count DESC LIMIT 10"
    ).fetchall()
    first = cur.execute("SELECT MIN(ts) FROM messages").fetchone()[0]
    last = cur.execute("SELECT MAX(ts) FROM messages").fetchone()[0]
    conn.close()
    return {
        "total_messages": total,
        "senders_count": len(senders),
        "messages_per_sender": [dict(r) for r in senders],
        "first_message_ts": first,
        "last_message_ts": last,
    }