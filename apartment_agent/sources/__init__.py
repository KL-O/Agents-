from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..models import Listing


class SourceAdapter(ABC):
    name: str = "unknown"

    @abstractmethod
    def search(self, area: str) -> List[Listing]:
        """Return listings for the given area. May raise on network/parsing errors --
        callers should catch per-source errors so one bad source doesn't kill a run."""
        raise NotImplementedError


def build_source(spec: str) -> SourceAdapter:
    """Build a source adapter from a CLI spec like 'mock', 'csv:path/to/file.csv', or
    'craigslist:newyork'."""
    from .csv_source import CSVSource
    from .craigslist import CraigslistRSSSource
    from .mock import MockSource

    name, _, arg = spec.partition(":")
    name = name.strip().lower()

    if name == "mock":
        return MockSource()
    if name == "csv":
        if not arg:
            raise ValueError("csv source requires a path, e.g. csv:sample_data/listings.csv")
        return CSVSource(arg)
    if name == "craigslist":
        if not arg:
            raise ValueError("craigslist source requires a subdomain, e.g. craigslist:newyork")
        return CraigslistRSSSource(arg)

    raise ValueError(f"Unknown source '{name}'. Known sources: mock, csv:<path>, craigslist:<subdomain>")
