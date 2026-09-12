import json
import tempfile
import unittest
from pathlib import Path

from sales_coach.models import Scenario, Transcript, Turn
from sales_coach.storage import ScenarioStore, save_transcript


class TestScenarioStore(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = ScenarioStore(self._tmp.name)

    def test_save_then_load_round_trips(self):
        scenario = Scenario(name="Skeptical Shopper", product_or_service="Headphones", customer_persona="Budget shopper")
        self.store.save(scenario)
        loaded = self.store.load("Skeptical Shopper")
        self.assertEqual(loaded, scenario)

    def test_save_uses_a_filesystem_safe_slug(self):
        scenario = Scenario(name="Returning Customer Upsell", product_or_service="Shoes", customer_persona="Regular")
        path = self.store.save(scenario)
        self.assertEqual(path.name, "returning_customer_upsell.json")

    def test_list_returns_sorted_names(self):
        self.store.save(Scenario(name="Zeta", product_or_service="x", customer_persona="y"))
        self.store.save(Scenario(name="Alpha", product_or_service="x", customer_persona="y"))
        self.assertEqual(self.store.list(), ["alpha", "zeta"])

    def test_load_missing_scenario_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.store.load("does not exist")


class TestSaveTranscript(unittest.TestCase):
    def test_writes_scenario_turns_and_feedback(self):
        scenario = Scenario(name="Test", product_or_service="Widget", customer_persona="Someone")
        transcript = Transcript(
            scenario=scenario,
            turns=[Turn("customer", "Hi, can I help you?"), Turn("trainee", "Just looking, thanks!")],
            feedback="Good opening, try asking a discovery question next.",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = save_transcript(transcript, tmp)
            self.assertTrue(path.exists())
            data = json.loads(path.read_text())
            self.assertEqual(data["scenario"]["name"], "Test")
            self.assertEqual(len(data["turns"]), 2)
            self.assertEqual(data["feedback"], "Good opening, try asking a discovery question next.")


if __name__ == "__main__":
    unittest.main()
