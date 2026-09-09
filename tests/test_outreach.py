import unittest

from apartment_agent.models import Listing, Requirements
from apartment_agent.outreach import draft_message


class TestDraftMessage(unittest.TestCase):
    def test_includes_subject_and_basic_question(self):
        listing = Listing(source="test", title="Cozy 1BR", price=1500, address="123 Main St")
        req = Requirements()
        draft = draft_message(listing, req)
        self.assertIn("Subject: Inquiry about Cozy 1BR", draft)
        self.assertIn("Is this unit still available?", draft)
        self.assertIn("123 Main St", draft)

    def test_asks_about_pets_when_required_but_unknown(self):
        listing = Listing(source="test", title="Studio", pet_friendly=None)
        req = Requirements(pet_friendly=True)
        draft = draft_message(listing, req)
        self.assertIn("Is it pet friendly?", draft)

    def test_does_not_ask_about_pets_when_already_confirmed(self):
        listing = Listing(source="test", title="Studio", pet_friendly=True)
        req = Requirements(pet_friendly=True)
        draft = draft_message(listing, req)
        self.assertNotIn("Is it pet friendly?", draft)

    def test_includes_extra_questions(self):
        listing = Listing(source="test", title="Loft")
        req = Requirements(extra_questions=["Is parking included?"])
        draft = draft_message(listing, req)
        self.assertIn("Is parking included?", draft)

    def test_signs_with_provided_name(self):
        listing = Listing(source="test", title="Loft")
        draft = draft_message(listing, Requirements(), your_name="Jordan")
        self.assertTrue(draft.strip().endswith("Jordan"))


if __name__ == "__main__":
    unittest.main()
