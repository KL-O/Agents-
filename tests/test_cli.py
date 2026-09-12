import io
import tempfile
import unittest
from contextlib import redirect_stdout

from sales_coach.cli import build_parser, cmd_scenarios_create, cmd_scenarios_list
from sales_coach.storage import ScenarioStore


class TestArgParsing(unittest.TestCase):
    def test_practice_defaults(self):
        parser = build_parser()
        args = parser.parse_args(["practice"])
        self.assertIsNone(args.scenario)
        self.assertFalse(args.save)
        self.assertEqual(args.func, __import__("sales_coach.cli", fromlist=["cmd_practice"]).cmd_practice)

    def test_practice_with_scenario_flag(self):
        parser = build_parser()
        args = parser.parse_args(["practice", "--scenario", "skeptical_budget_shopper"])
        self.assertEqual(args.scenario, "skeptical_budget_shopper")

    def test_scenarios_list_subcommand(self):
        parser = build_parser()
        args = parser.parse_args(["scenarios", "list"])
        self.assertEqual(args.func, cmd_scenarios_list)

    def test_scenarios_create_subcommand(self):
        parser = build_parser()
        args = parser.parse_args(["scenarios", "create"])
        self.assertEqual(args.func, cmd_scenarios_create)

    def test_missing_command_is_required(self):
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args([])


class TestScenariosListCommand(unittest.TestCase):
    def test_lists_saved_scenarios(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ScenarioStore(tmp)
            from sales_coach.models import Scenario

            store.save(Scenario(name="Alpha", product_or_service="x", customer_persona="y"))

            parser = build_parser()
            args = parser.parse_args(["--scenarios-dir", tmp, "scenarios", "list"])

            buf = io.StringIO()
            with redirect_stdout(buf):
                args.func(args)

            self.assertIn("alpha", buf.getvalue())

    def test_empty_directory_prints_notice(self):
        with tempfile.TemporaryDirectory() as tmp:
            parser = build_parser()
            args = parser.parse_args(["--scenarios-dir", tmp, "scenarios", "list"])

            buf = io.StringIO()
            with redirect_stdout(buf):
                args.func(args)

            self.assertIn("No scenarios saved", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
