from __future__ import annotations

from typing import List

from ..models import Listing
from . import SourceAdapter

# Deterministic sample listings so the whole pipeline (search -> match -> draft -> store)
# can be exercised end-to-end without a real, ToS-compliant data source wired in yet.
# Swap in a real SourceAdapter (see csv_source.py, craigslist.py) once you have one.
_TEMPLATES = [
    dict(
        source="zillow-mock", title="Sunny 1BR near downtown", price=1650, bedrooms=1,
        bathrooms=1, sqft=700, pet_friendly=True, available_date="2026-10-01",
        description="Bright 1 bedroom with in-unit laundry and a small balcony.",
        contact_name="Dana", contact_email="dana@example.com",
    ),
    dict(
        source="facebook-mock", title="Cozy studio, walk to everything", price=1200,
        bedrooms=0, bathrooms=1, sqft=450, pet_friendly=False, available_date="2026-09-15",
        description="Studio apartment, no pets, street parking only.",
        contact_name="Marcus", contact_phone="555-0101",
    ),
    dict(
        source="craigslist-mock", title="Spacious 2BR/2BA with parking", price=2100,
        bedrooms=2, bathrooms=2, sqft=1050, pet_friendly=True, available_date="2026-11-01",
        description="Two bedroom, two bath, in-unit laundry, assigned parking, pet friendly.",
        contact_email="listings@example-property.com",
    ),
    dict(
        source="zillow-mock", title="Luxury 2BR high-rise", price=3200, bedrooms=2,
        bathrooms=2, sqft=1200, pet_friendly=False, available_date="2026-10-15",
        description="High-rise unit with gym and rooftop deck. No pets allowed.",
        contact_name="Priya",
    ),
    dict(
        source="facebook-mock", title="Affordable 1BR, utilities included", price=1400,
        bedrooms=1, bathrooms=1, sqft=600, pet_friendly=None, available_date=None,
        description="1 bedroom apartment, utilities included, pet policy unknown -- ask.",
        contact_name="Lee",
    ),
]


class MockSource(SourceAdapter):
    name = "mock"

    def search(self, area: str) -> List[Listing]:
        listings = []
        for tmpl in _TEMPLATES:
            data = dict(tmpl)
            data["address"] = f"{data.pop('title')} - {area}"
            title = tmpl["title"]
            data["area"] = area
            data["external_id"] = f"{data['source']}:{area}:{title}"
            listings.append(Listing(title=title, **data))
        return listings
