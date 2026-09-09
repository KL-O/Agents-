from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from .models import Listing

_SCHEMA = """
CREATE TABLE IF NOT EXISTS listings (
    id TEXT PRIMARY KEY,
    source TEXT,
    title TEXT,
    url TEXT,
    address TEXT,
    area TEXT,
    price REAL,
    bedrooms REAL,
    bathrooms REAL,
    sqft REAL,
    pet_friendly INTEGER,
    available_date TEXT,
    description TEXT,
    contact_name TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    extra_json TEXT,
    status TEXT DEFAULT 'new',
    score REAL,
    first_seen TEXT,
    last_seen TEXT
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bool_to_int(value: Optional[bool]) -> Optional[int]:
    return None if value is None else int(value)


def _int_to_bool(value: Optional[int]) -> Optional[bool]:
    return None if value is None else bool(value)


class Store:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(_SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def upsert(self, listing: Listing) -> bool:
        """Insert a new listing or refresh a previously seen one. Returns True if this
        listing id hadn't been seen before."""
        existing = self.conn.execute("SELECT id FROM listings WHERE id = ?", (listing.id,)).fetchone()
        now = _now()
        if existing:
            self.conn.execute(
                """UPDATE listings SET price=?, description=?, last_seen=? WHERE id=?""",
                (listing.price, listing.description, now, listing.id),
            )
            self.conn.commit()
            return False

        self.conn.execute(
            """INSERT INTO listings (
                id, source, title, url, address, area, price, bedrooms, bathrooms, sqft,
                pet_friendly, available_date, description, contact_name, contact_email,
                contact_phone, extra_json, status, first_seen, last_seen
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'new', ?, ?)""",
            (
                listing.id,
                listing.source,
                listing.title,
                listing.url,
                listing.address,
                listing.area,
                listing.price,
                listing.bedrooms,
                listing.bathrooms,
                listing.sqft,
                _bool_to_int(listing.pet_friendly),
                listing.available_date,
                listing.description,
                listing.contact_name,
                listing.contact_email,
                listing.contact_phone,
                json.dumps(listing.extra),
                now,
                now,
            ),
        )
        self.conn.commit()
        return True

    def update_status(self, listing_id: str, status: str) -> None:
        self.conn.execute("UPDATE listings SET status=? WHERE id=?", (status, listing_id))
        self.conn.commit()

    def update_score(self, listing_id: str, score: float) -> None:
        self.conn.execute("UPDATE listings SET score=? WHERE id=?", (score, listing_id))
        self.conn.commit()

    def get(self, listing_id: str) -> Optional[Listing]:
        row = self.conn.execute("SELECT * FROM listings WHERE id=?", (listing_id,)).fetchone()
        return self._row_to_listing(row) if row else None

    def list(self, status: Optional[str] = None):
        if status:
            rows = self.conn.execute("SELECT * FROM listings WHERE status=? ORDER BY score DESC", (status,)).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM listings ORDER BY score DESC").fetchall()
        return [self._row_to_listing(row) for row in rows]

    @staticmethod
    def _row_to_listing(row: sqlite3.Row) -> Listing:
        return Listing(
            id=row["id"],
            source=row["source"],
            title=row["title"],
            url=row["url"],
            address=row["address"],
            area=row["area"],
            price=row["price"],
            bedrooms=row["bedrooms"],
            bathrooms=row["bathrooms"],
            sqft=row["sqft"],
            pet_friendly=_int_to_bool(row["pet_friendly"]),
            available_date=row["available_date"],
            description=row["description"] or "",
            contact_name=row["contact_name"],
            contact_email=row["contact_email"],
            contact_phone=row["contact_phone"],
            extra=json.loads(row["extra_json"]) if row["extra_json"] else {},
        )
