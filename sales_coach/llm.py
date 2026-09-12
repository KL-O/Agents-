from __future__ import annotations

from typing import Dict, List, Optional, Protocol


class ChatClient(Protocol):
    def complete(self, system: str, messages: List[Dict[str, str]]) -> str: ...


class AnthropicChatClient:
    """Talks to the Anthropic API. Requires the `anthropic` package and an API key
    (passed explicitly or via the ANTHROPIC_API_KEY environment variable)."""

    def __init__(self, model: str = "claude-sonnet-5", api_key: Optional[str] = None, max_tokens: int = 1024):
        import anthropic  # imported lazily so the dependency is only needed when actually calling the API

        self._client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def complete(self, system: str, messages: List[Dict[str, str]]) -> str:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=messages,
        )
        return "".join(block.text for block in response.content if getattr(block, "type", None) == "text")
