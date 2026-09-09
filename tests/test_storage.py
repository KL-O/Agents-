import tempfile
import unittest
from pathlib import Path

from apartment_agent.models import Listing
from apartment_agent.storage import Store


class TestStore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.store = Store(self.tmp.name)

    def tearDown(self):
        self.store.close()
        Path(self.tmp.name).unlink(missing_ok=True)

    def test_upsert_reports_new_then_not_new(self):
        listing = Listing(source="test", title="1BR", external_id="abc123", price=1500)
        self.assertTrue(self.store.upsert(listing))
        self.assertFalse(self.store.upsert(listing))

    def test_status_updates_persist(self):
        listing = Listing(source="test", title="1BR", external_id="abc123")
        self.store.upsert(listing)
        self.store.update_status(listing.id, "contacted")
        fetched = self.store.get(listing.id)
        self.assertEqual(self.store.list(status="contacted")[0].id, listing.id)
        self.assertEqual(fetched.id, listing.id)

    def test_list_filters_by_status(self):
        a = Listing(source="test", title="A", external_id="a")
        b = Listing(source="test", title="B", external_id="b")
        self.store.upsert(a)
        self.store.upsert(b)
        self.store.update_status(a.id, "rejected")
        new_only = self.store.list(status="new")
        self.assertEqual(len(new_only), 1)
        self.assertEqual(new_only[0].id, b.id)


if __name__ == "__main__":
    unittest.main()
