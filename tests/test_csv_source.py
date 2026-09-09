import csv
import tempfile
import unittest
from pathlib import Path

from apartment_agent.sources.csv_source import CSVSource

ROWS = [
    dict(
        source="zillow", title="Austin 1BR", url="http://example.com/1",
        address="123 Main St, Austin, TX", price="1500", bedrooms="1", bathrooms="1",
        sqft="700", pet_friendly="true", available_date="2026-10-01",
        description="laundry, parking", contact_name="Alex", contact_email="alex@example.com",
        contact_phone="",
    ),
    dict(
        source="facebook", title="Denver 2BR", url="http://example.com/2",
        address="456 Oak Ave, Denver, CO", price="1800", bedrooms="2", bathrooms="1",
        sqft="900", pet_friendly="", available_date="", description="near the park",
        contact_name="", contact_email="", contact_phone="555-0102",
    ),
]


class TestCSVSource(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="")
        writer = csv.DictWriter(self.tmp, fieldnames=list(ROWS[0].keys()))
        writer.writeheader()
        writer.writerows(ROWS)
        self.tmp.close()

    def tearDown(self):
        Path(self.tmp.name).unlink(missing_ok=True)

    def test_filters_by_area(self):
        source = CSVSource(self.tmp.name)
        results = source.search("Austin, TX")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Austin 1BR")
        self.assertTrue(results[0].pet_friendly)

    def test_other_area_returns_other_listing(self):
        source = CSVSource(self.tmp.name)
        results = source.search("Denver")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Denver 2BR")
        self.assertIsNone(results[0].pet_friendly)


if __name__ == "__main__":
    unittest.main()
