import unittest

from sales_coach.models import Scenario
from sales_coach.session import PracticeSession, coach_system_prompt, customer_system_prompt


class FakeChatClient:
    def __init__(self, replies):
        self._replies = list(replies)
        self.calls = []

    def complete(self, system, messages):
        self.calls.append((system, messages))
        return self._replies.pop(0)


def make_scenario(**overrides):
    defaults = dict(
        name="Skeptical Budget Shopper",
        product_or_service="Headphones ($249)",
        customer_persona="A budget-conscious shopper",
        personality_traits=["price-sensitive", "guarded"],
        objections_focus=["price is too high"],
        difficulty="medium",
        goal="Build value before mentioning price",
    )
    defaults.update(overrides)
    return Scenario(**defaults)


class TestPrompts(unittest.TestCase):
    def test_customer_prompt_includes_persona_and_objections(self):
        prompt = customer_system_prompt(make_scenario())
        self.assertIn("Headphones ($249)", prompt)
        self.assertIn("budget-conscious shopper", prompt)
        self.assertIn("price is too high", prompt)

    def test_coach_prompt_includes_goal(self):
        prompt = coach_system_prompt(make_scenario())
        self.assertIn("Build value before mentioning price", prompt)


class TestPracticeSession(unittest.TestCase):
    def test_opening_line_records_customer_turn(self):
        client = FakeChatClient(["Hi there, just browsing."])
        session = PracticeSession(make_scenario(), client)

        opening = session.opening_line()

        self.assertEqual(opening, "Hi there, just browsing.")
        self.assertEqual(len(session.transcript.turns), 1)
        self.assertEqual(session.transcript.turns[0].role, "customer")

    def test_say_appends_trainee_then_customer_turn_and_maps_roles(self):
        client = FakeChatClient(["Hi there!", "These seem pricey though."])
        session = PracticeSession(make_scenario(), client)
        session.opening_line()

        reply = session.say("Hi! What brings you in today?")

        self.assertEqual(reply, "These seem pricey though.")
        roles = [t.role for t in session.transcript.turns]
        self.assertEqual(roles, ["customer", "trainee", "customer"])

        # second call's message history should map trainee -> user, customer -> assistant
        _, messages = client.calls[1]
        self.assertEqual(
            messages,
            [
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "Hi! What brings you in today?"},
            ],
        )

    def test_hint_does_not_mutate_transcript(self):
        client = FakeChatClient(["Hi there!", "Try asking what matters most to them about the purchase."])
        session = PracticeSession(make_scenario(), client)
        session.opening_line()

        hint = session.hint()

        self.assertIn("asking what matters most", hint)
        self.assertEqual(len(session.transcript.turns), 1)

    def test_feedback_is_stored_on_transcript(self):
        client = FakeChatClient(["Hi there!", "Nice opening, ask a follow-up question next time."])
        session = PracticeSession(make_scenario(), client)
        session.opening_line()

        feedback = session.feedback()

        self.assertEqual(session.transcript.feedback, feedback)
        self.assertIn("Nice opening", feedback)


if __name__ == "__main__":
    unittest.main()
