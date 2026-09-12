import unittest

from sales_coach.models import Scenario


class TestScenario(unittest.TestCase):
    def test_round_trip_through_dict(self):
        scenario = Scenario(
            name="Test scenario",
            product_or_service="Running shoes",
            customer_persona="A repeat customer in a hurry",
            personality_traits=["friendly", "hurried"],
            objections_focus=["doesn't need anything extra"],
            difficulty="easy",
            goal="Practice a light upsell",
            notes="Some notes",
        )
        restored = Scenario.from_dict(scenario.to_dict())
        self.assertEqual(restored, scenario)

    def test_from_dict_fills_in_defaults(self):
        restored = Scenario.from_dict({"name": "Minimal"})
        self.assertEqual(restored.name, "Minimal")
        self.assertEqual(restored.product_or_service, "")
        self.assertEqual(restored.personality_traits, [])
        self.assertEqual(restored.objections_focus, [])
        self.assertEqual(restored.difficulty, "medium")


if __name__ == "__main__":
    unittest.main()
