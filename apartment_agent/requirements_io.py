from __future__ import annotations

import json
from pathlib import Path

from .models import Requirements

_FIELDS = {
    "areas",
    "min_price",
    "max_price",
    "min_bedrooms",
    "max_bedrooms",
    "min_bathrooms",
    "min_sqft",
    "pet_friendly",
    "move_in_by",
    "must_have_keywords",
    "exclude_keywords",
    "preferred_keywords",
    "extra_questions",
}


def load_requirements(path: str) -> Requirements:
    data = json.loads(Path(path).read_text())
    unknown = set(data) - _FIELDS
    if unknown:
        raise ValueError(f"Unknown fields in requirements file: {sorted(unknown)}")
    return Requirements(**data)
