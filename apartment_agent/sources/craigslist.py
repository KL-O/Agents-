from __future__ import annotations

import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import List, Optional

from ..models import Listing
from . import SourceAdapter

_PRICE_RE = re.compile(r"\$([\d,]+)")
_BEDROOM_RE = re.compile(r"(\d+)\s*br\b", re.IGNORECASE)


def parse_rss(xml_text: str, area: str) -> List[Listing]:
    """Parse Craigslist's public search-results RSS feed. Split out from fetch_rss so it
    can be unit tested against a fixture without hitting the network."""
    root = ET.fromstring(xml_text)
    listings = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip() or None
        description = (item.findtext("description") or "").strip()

        price: Optional[float] = None
        price_match = _PRICE_RE.search(title)
        if price_match:
            price = float(price_match.group(1).replace(",", ""))

        bedrooms: Optional[float] = None
        bed_match = _BEDROOM_RE.search(title)
        if bed_match:
            bedrooms = float(bed_match.group(1))

        listings.append(
            Listing(
                source="craigslist",
                title=title or "Untitled listing",
                url=link,
                address=None,
                area=area,
                price=price,
                bedrooms=bedrooms,
                description=description,
                # Craigslist's RSS feed doesn't expose contact info; replying happens
                # through the listing's own reply-by-email relay on the page at `url`.
            )
        )
    return listings


class CraigslistRSSSource(SourceAdapter):
    """Uses Craigslist's own public RSS search feed (a feature they intentionally expose
    for search results, not scraping the site's HTML), so this stays within normal use."""

    name = "craigslist"

    def __init__(self, subdomain: str, category: str = "apa", timeout: float = 15.0):
        self.subdomain = subdomain
        self.category = category
        self.timeout = timeout

    def search(self, area: str) -> List[Listing]:
        query = urllib.parse.urlencode({"format": "rss", "query": area})
        url = f"https://{self.subdomain}.craigslist.org/search/{self.category}?{query}"
        req = urllib.request.Request(url, headers={"User-Agent": "apartment-search-agent/1.0"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            xml_text = resp.read().decode("utf-8", errors="replace")
        return parse_rss(xml_text, area)
