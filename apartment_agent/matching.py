from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from .models import Listing, MatchResult, Requirements


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def score_listing(listing: Listing, req: Requirements) -> MatchResult:
    """Apply hard requirements as pass/fail filters, then rank passing listings by
    how well they satisfy the softer, "nice to have" criteria."""
    matched: list = []
    failed: list = []
    text = f"{listing.title} {listing.description}".lower()

    if req.min_price is not None and listing.price is not None:
        if listing.price < req.min_price:
            failed.append(f"price ${listing.price:g} is below minimum ${req.min_price:g}")
        else:
            matched.append(f"price meets minimum ${req.min_price:g}")
    if req.max_price is not None and listing.price is not None:
        if listing.price > req.max_price:
            failed.append(f"price ${listing.price:g} exceeds maximum ${req.max_price:g}")
        else:
            matched.append(f"price within budget (max ${req.max_price:g})")

    if req.min_bedrooms is not None and listing.bedrooms is not None:
        if listing.bedrooms < req.min_bedrooms:
            failed.append(f"only {listing.bedrooms:g} bedrooms, need at least {req.min_bedrooms:g}")
        else:
            matched.append("meets minimum bedrooms")
    if req.max_bedrooms is not None and listing.bedrooms is not None:
        if listing.bedrooms > req.max_bedrooms:
            failed.append(f"{listing.bedrooms:g} bedrooms exceeds max {req.max_bedrooms:g}")

    if req.min_bathrooms is not None and listing.bathrooms is not None:
        if listing.bathrooms < req.min_bathrooms:
            failed.append(f"only {listing.bathrooms:g} bathrooms, need at least {req.min_bathrooms:g}")
        else:
            matched.append("meets minimum bathrooms")

    if req.min_sqft is not None and listing.sqft is not None:
        if listing.sqft < req.min_sqft:
            failed.append(f"only {listing.sqft:g} sqft, need at least {req.min_sqft:g}")
        else:
            matched.append("meets minimum square footage")

    if req.pet_friendly is True and listing.pet_friendly is False:
        failed.append("listing is not pet friendly")
    elif req.pet_friendly is True and listing.pet_friendly is True:
        matched.append("confirmed pet friendly")

    move_in_by = _parse_date(req.move_in_by)
    available = _parse_date(listing.available_date)
    if move_in_by and available and available > move_in_by:
        failed.append(f"not available until {available.isoformat()}, after your {move_in_by.isoformat()} deadline")
    elif move_in_by and available:
        matched.append("available in time")

    missing_required = [kw for kw in req.must_have_keywords if kw.lower() not in text]
    if missing_required:
        failed.append(f"missing required feature(s): {', '.join(missing_required)}")
    elif req.must_have_keywords:
        matched.append("has all required features")

    present_excluded = [kw for kw in req.exclude_keywords if kw.lower() in text]
    if present_excluded:
        failed.append(f"contains excluded term(s): {', '.join(present_excluded)}")

    passes = not failed

    score = 0.5
    if req.preferred_keywords:
        hits = [kw for kw in req.preferred_keywords if kw.lower() in text]
        for kw in hits:
            matched.append(f"has preferred feature: {kw}")
        score += 0.3 * (len(hits) / len(req.preferred_keywords))
    else:
        score += 0.15

    if req.max_price is not None and listing.price is not None:
        floor = req.min_price or 0.0
        span = max(req.max_price - floor, 1.0)
        score += 0.2 * _clamp((req.max_price - listing.price) / span)
    else:
        score += 0.1

    if req.min_sqft is not None and listing.sqft is not None and listing.sqft > req.min_sqft:
        score += 0.1 * _clamp((listing.sqft - req.min_sqft) / req.min_sqft)

    score = _clamp(score)

    return MatchResult(listing=listing, passes=passes, score=score, matched_reasons=matched, failed_reasons=failed)


def filter_listings(listings, req: Requirements):
    """Score every listing and return results sorted best-first (passing listings before
    rejected ones, then by score)."""
    results = [score_listing(listing, req) for listing in listings]
    results.sort(key=lambda r: (not r.passes, -r.score))
    return results
