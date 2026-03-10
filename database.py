"""
ArthSakshar AI – Database Layer
SQLite database for call logs, campaigns, and events.
"""

import aiosqlite
import os
from config import settings

DB_PATH = settings.DATABASE_PATH


async def init_db():
    """Initialize database tables."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_sid TEXT UNIQUE,
                phone_number TEXT,
                ca_name TEXT DEFAULT '',
                city TEXT DEFAULT '',
                language TEXT DEFAULT 'en',
                status TEXT DEFAULT 'initiated',
                duration INTEGER DEFAULT 0,
                transferred INTEGER DEFAULT 0,
                interested INTEGER DEFAULT 0,
                callback_requested INTEGER DEFAULT 0,
                conversation_log TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                total_calls INTEGER DEFAULT 0,
                completed_calls INTEGER DEFAULT 0,
                answered_calls INTEGER DEFAULT 0,
                transferred_calls INTEGER DEFAULT 0,
                interested_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                event_date TEXT NOT NULL,
                venue TEXT NOT NULL,
                coordinator_name TEXT NOT NULL,
                coordinator_phone TEXT NOT NULL,
                description TEXT DEFAULT '',
                is_active INTEGER DEFAULT 1
            )
        """)

        # Insert sample Maharashtra events
        existing = await db.execute("SELECT COUNT(*) FROM events")
        count = await existing.fetchone()
        if count[0] == 0:
            sample_events = [
                ("Mumbai", "2026-03-20", "WIRC Auditorium, Andheri", "CA Priya Deshmukh", "+919876543001", "Budget Literacy Workshop - Mumbai Central"),
                ("Pune", "2026-03-22", "ICAI Bhawan, Deccan", "CA Rahul Kulkarni", "+919876543002", "Budget Literacy Workshop - Pune Chapter"),
                ("Nagpur", "2026-03-25", "CA Bhawan, Dharampeth", "CA Sneha Wankhede", "+919876543003", "Budget Literacy Workshop - Nagpur"),
                ("Nashik", "2026-03-27", "Hotel Express Inn", "CA Amit Joshi", "+919876543004", "Budget Literacy Workshop - Nashik"),
                ("Aurangabad", "2026-03-29", "MGM Campus Hall", "CA Meera Patil", "+919876543005", "Budget Literacy Workshop - Aurangabad"),
                ("Kolhapur", "2026-04-01", "Shahu Smarak Bhawan", "CA Vijay Chavan", "+919876543006", "Budget Literacy Workshop - Kolhapur"),
                ("Thane", "2026-04-03", "Thane CA Association Hall", "CA Anita Sawant", "+919876543007", "Budget Literacy Workshop - Thane"),
                ("Solapur", "2026-04-05", "Walchand College Hall", "CA Sanjay Mane", "+919876543008", "Budget Literacy Workshop - Solapur"),
                ("Sangli", "2026-04-07", "Town Hall, Sangli", "CA Rekha Jadhav", "+919876543009", "Budget Literacy Workshop - Sangli"),
                ("Amravati", "2026-04-10", "Hanuman Vyayam Prasarak Hall", "CA Deepak Ingole", "+919876543010", "Budget Literacy Workshop - Amravati"),
            ]
            await db.executemany(
                "INSERT INTO events (city, event_date, venue, coordinator_name, coordinator_phone, description) VALUES (?, ?, ?, ?, ?, ?)",
                sample_events
            )

        await db.commit()


async def log_call(call_sid: str, phone_number: str, ca_name: str = "", city: str = "", language: str = "en"):
    """Log a new call."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO calls (call_sid, phone_number, ca_name, city, language) VALUES (?, ?, ?, ?, ?)",
            (call_sid, phone_number, ca_name, city, language)
        )
        await db.commit()


async def update_call(call_sid: str, **kwargs):
    """Update call record."""
    if not kwargs:
        return
    set_clause = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values()) + [call_sid]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE calls SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE call_sid = ?",
            values
        )
        await db.commit()


async def get_calls(limit: int = 50):
    """Get recent call logs."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM calls ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_events(city: str = None):
    """Get events, optionally filtered by city."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if city:
            cursor = await db.execute(
                "SELECT * FROM events WHERE is_active = 1 AND LOWER(city) = LOWER(?) ORDER BY event_date",
                (city,)
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM events WHERE is_active = 1 ORDER BY event_date"
            )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_campaigns():
    """Get all campaigns."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM campaigns ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def create_campaign(name: str, total_calls: int):
    """Create a new campaign."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO campaigns (name, total_calls) VALUES (?, ?)",
            (name, total_calls)
        )
        await db.commit()
        return cursor.lastrowid


async def update_campaign(campaign_id: int, **kwargs):
    """Update campaign record."""
    if not kwargs:
        return
    set_clause = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values()) + [campaign_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE campaigns SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            values
        )
        await db.commit()


async def get_dashboard_stats():
    """Get aggregated stats for the dashboard."""
    async with aiosqlite.connect(DB_PATH) as db:
        stats = {}

        cursor = await db.execute("SELECT COUNT(*) FROM calls")
        row = await cursor.fetchone()
        stats["total_calls"] = row[0]

        cursor = await db.execute("SELECT COUNT(*) FROM calls WHERE status = 'completed'")
        row = await cursor.fetchone()
        stats["completed_calls"] = row[0]

        cursor = await db.execute("SELECT COUNT(*) FROM calls WHERE transferred = 1")
        row = await cursor.fetchone()
        stats["transferred_calls"] = row[0]

        cursor = await db.execute("SELECT COUNT(*) FROM calls WHERE interested = 1")
        row = await cursor.fetchone()
        stats["interested_count"] = row[0]

        cursor = await db.execute("SELECT COUNT(*) FROM calls WHERE callback_requested = 1")
        row = await cursor.fetchone()
        stats["callback_requests"] = row[0]

        cursor = await db.execute("SELECT COUNT(DISTINCT city) FROM calls WHERE city != ''")
        row = await cursor.fetchone()
        stats["cities_reached"] = row[0]

        cursor = await db.execute("SELECT COUNT(*) FROM events WHERE is_active = 1")
        row = await cursor.fetchone()
        stats["active_events"] = row[0]

        return stats
