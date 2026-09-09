from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Optional


def make_listing_id(
    source: str,
    external_id: Optional[str] = None,
    url: Optional[str] = None,
    title: str = "",
    address: str = "",
    price: Optional[float] = None,
) -> str:
    """Build a stable id so the same listing dedupes across repeated runs."""
    if external_id:
        basis = f"ext:{external_id}"
    elif url:
        basis = f"url:{url}"
    else:
        basis = f"fallback:{title}|{address}|{price}"
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:16]
    return f"{source}:{digest}"


@dataclass
class Listing:
    source: str
    title: str
    id: str = ""
    external_id: Optional[str] = None
    url: Optional[str] = None
    address: Optional[str] = None
    area: Optional[str] = None
    price: Optional[float] = None
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    sqft: Optional[float] = None
    pet_friendly: Optional[bool] = None
    available_date: Optional[str] = None
    description: str = ""
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    posted_at: Optional[str] = None
    extra: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = make_listing_id(
                self.source,
                external_id=self.external_id,
                url=self.url,
                title=self.title,
                address=self.address or "",
                price=self.price,
            )


@dataclass
class Requirements:
    areas: list = field(default_factory=list)
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_bedrooms: Optional[float] = None
    max_bedrooms: Optional[float] = None
    min_bathrooms: Optional[float] = None
    min_sqft: Optional[float] = None
    pet_friendly: Optional[bool] = None
    move_in_by: Optional[str] = None
    must_have_keywords: list = field(default_factory=list)
    exclude_keywords: list = field(default_factory=list)
    preferred_keywords: list = field(default_factory=list)
    extra_questions: list = field(default_factory=list)


@dataclass
class MatchResult:
    listing: Listing
    passes: bool
    score: float
    matched_reasons: list = field(default_factory=list)
    failed_reasons: list = field(default_factory=list)
