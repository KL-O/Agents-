from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import List, Optional

from ..models import Listing
from . import SourceAdapter


def _area_tokens(area: str) -> List[str]:
    return [tok for tok in re.split(r"[^a-z0-9]+", area.lower()) if len(tok) > 2]


def _parse_float(value: Optional[str]) -> Optional[float]:
    if value is None or value.strip() == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _parse_bool(value: Optional[str]) -> Optional[bool]:
    if value is None or value.strip() == "":
        return None
    return value.strip().lower() in ("true", "yes", "1", "y")


class CSVSource(SourceAdapter):
    """Import listings you (or a browser extension/copy-paste) gathered manually from
    Zillow, Facebook Marketplace, or anywhere else that doesn't offer an API and can't be
    scraped without violating its Terms of Service or a login wall. Expected columns:
    source,title,url,address,price,bedrooms,bathrooms,sqft,pet_friendly,available_date,
    description,contact_name,contact_email,contact_phone
    """

    name = "csv"

    def __init__(self, path: str):
        self.path = path

    def search(self, area: str) -> List[Listing]:
        tokens = _area_tokens(area)
        listings = []
        with Path(self.path).open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                haystack = f"{row.get('address', '')} {row.get('title', '')}".lower()
                if tokens and not any(tok in haystack for tok in tokens):
                    continue
                listings.append(
                    Listing(
                        source=row.get("source") or "csv-import",
                        title=row.get("title", "").strip() or "Untitled listing",
                        url=row.get("url") or None,
                        address=row.get("address") or None,
                        area=area,
                        price=_parse_float(row.get("price")),
                        bedrooms=_parse_float(row.get("bedrooms")),
                        bathrooms=_parse_float(row.get("bathrooms")),
                        sqft=_parse_float(row.get("sqft")),
                        pet_friendly=_parse_bool(row.get("pet_friendly")),
                        available_date=row.get("available_date") or None,
                        description=row.get("description", ""),
                        contact_name=row.get("contact_name") or None,
                        contact_email=row.get("contact_email") or None,
                        contact_phone=row.get("contact_phone") or None,
                    )
                )
        return listings
