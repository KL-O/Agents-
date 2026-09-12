import sys
import types
import unittest


class TestAnthropicChatClient(unittest.TestCase):
    def setUp(self):
        # Stub out the `anthropic` package so this test doesn't need it installed
        # or a real API key; sales_coach.llm imports it lazily inside __init__.
        self._fake_module = types.ModuleType("anthropic")
        self._captured = {}

        class FakeTextBlock:
            def __init__(self, text):
                self.type = "text"
                self.text = text

        class FakeMessages:
            def create(self, **kwargs):
                self._captured_kwargs = kwargs
                TestAnthropicChatClient._last_create_kwargs = kwargs
                return types.SimpleNamespace(content=[FakeTextBlock("mocked reply")])

        class FakeAnthropic:
            def __init__(self, api_key=None):
                self.api_key = api_key
                self.messages = FakeMessages()

        self._fake_module.Anthropic = FakeAnthropic
        self._original = sys.modules.get("anthropic")
        sys.modules["anthropic"] = self._fake_module

    def tearDown(self):
        if self._original is not None:
            sys.modules["anthropic"] = self._original
        else:
            sys.modules.pop("anthropic", None)

    def test_complete_forwards_args_and_extracts_text(self):
        from sales_coach.llm import AnthropicChatClient

        client = AnthropicChatClient(model="claude-sonnet-5", api_key="test-key")
        result = client.complete("system prompt", [{"role": "user", "content": "hi"}])

        self.assertEqual(result, "mocked reply")
        kwargs = TestAnthropicChatClient._last_create_kwargs
        self.assertEqual(kwargs["model"], "claude-sonnet-5")
        self.assertEqual(kwargs["system"], "system prompt")
        self.assertEqual(kwargs["messages"], [{"role": "user", "content": "hi"}])


if __name__ == "__main__":
    unittest.main()
