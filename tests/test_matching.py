import unittest

from apartment_agent.matching import filter_listings, score_listing
from apartment_agent.models import Listing, Requirements


def make_listing(**overrides):
    defaults = dict(
        source="test",
        title="Nice 1BR with laundry",
        price=1500,
        bedrooms=1,
        bathrooms=1,
        sqft=700,
        pet_friendly=True,
        available_date="2026-10-01",
        description="In-unit laundry, quiet street, parking available.",
    )
    defaults.update(overrides)
    return Listing(**defaults)


class TestScoreListing(unittest.TestCase):
    def test_passes_when_all_hard_requirements_met(self):
        req = Requirements(max_price=2000, min_bedrooms=1, must_have_keywords=["laundry"])
        result = score_listing(make_listing(), req)
        self.assertTrue(result.passes)
        self.assertEqual(result.failed_reasons, [])

    def test_fails_over_budget(self):
        req = Requirements(max_price=1000)
        result = score_listing(make_listing(price=1500), req)
        self.assertFalse(result.passes)
        self.assertTrue(any("exceeds maximum" in r for r in result.failed_reasons))

    def test_fails_missing_required_keyword(self):
        req = Requirements(must_have_keywords=["dishwasher"])
        result = score_listing(make_listing(), req)
        self.assertFalse(result.passes)
        self.assertTrue(any("dishwasher" in r for r in result.failed_reasons))

    def test_fails_on_excluded_keyword(self):
        req = Requirements(exclude_keywords=["no pets"])
        result = score_listing(make_listing(description="Sorry, no pets allowed."), req)
        self.assertFalse(result.passes)

    def test_fails_when_not_pet_friendly_but_required(self):
        req = Requirements(pet_friendly=True)
        result = score_listing(make_listing(pet_friendly=False), req)
        self.assertFalse(result.passes)

    def test_unknown_pet_status_does_not_fail(self):
        req = Requirements(pet_friendly=True)
        result = score_listing(make_listing(pet_friendly=None), req)
        self.assertTrue(result.passes)

    def test_fails_available_after_move_in_deadline(self):
        req = Requirements(move_in_by="2026-09-01")
        result = score_listing(make_listing(available_date="2026-10-01"), req)
        self.assertFalse(result.passes)

    def test_missing_data_is_not_penalized(self):
        req = Requirements(max_price=2000, min_sqft=500)
        result = score_listing(make_listing(price=None, sqft=None), req)
        self.assertTrue(result.passes)


class TestFilterListings(unittest.TestCase):
    def test_passing_listings_sort_before_rejected_and_by_score(self):
        req = Requirements(max_price=2000, preferred_keywords=["parking", "balcony"])
        cheap_with_parking = make_listing(price=1200, description="parking included, laundry")
        expensive_no_extras = make_listing(price=1900, description="laundry only")
        over_budget = make_listing(price=5000)

        results = filter_listings([over_budget, expensive_no_extras, cheap_with_parking], req)

        self.assertTrue(results[0].passes and results[1].passes)
        self.assertFalse(results[2].passes)
        self.assertGreaterEqual(results[0].score, results[1].score)


if __name__ == "__main__":
    unittest.main()
