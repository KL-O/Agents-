from __future__ import annotations

from .llm import ChatClient
from .models import Scenario, Transcript, Turn


def customer_system_prompt(scenario: Scenario) -> str:
    traits = ", ".join(scenario.personality_traits) or "no particular quirks"
    objections = ", ".join(scenario.objections_focus) or "whatever feels natural for this kind of shopper"
    return (
        "You are role-playing as a customer in a retail sales training exercise. "
        "A beginner salesperson is practicing on you. Stay in character as the customer "
        "only, respond the way a real person would speak out loud (1-4 sentences), and "
        "never break character to give sales advice or acknowledge this is a simulation.\n\n"
        f"Product or service being sold: {scenario.product_or_service}\n"
        f"Who you are: {scenario.customer_persona}\n"
        f"Personality traits to play: {traits}\n"
        f"Objections to raise naturally over the course of the conversation: {objections}\n"
        f"Difficulty: {scenario.difficulty}"
    )


def coach_system_prompt(scenario: Scenario) -> str:
    return (
        "You are an expert retail sales coach mentoring a beginner. They are practicing "
        "a roleplay against a simulated customer. Be specific, concrete, and encouraging; "
        "quote their actual lines when pointing something out.\n\n"
        f"Scenario: {scenario.name}\n"
        f"Product or service: {scenario.product_or_service}\n"
        f"Customer: {scenario.customer_persona}\n"
        f"Goal for the trainee: {scenario.goal or 'build rapport, understand the customer, and handle objections well'}"
    )


class PracticeSession:
    def __init__(self, scenario: Scenario, chat_client: ChatClient):
        self.scenario = scenario
        self.chat_client = chat_client
        self.transcript = Transcript(scenario=scenario)

    def _customer_messages(self) -> list:
        messages = []
        for turn in self.transcript.turns:
            role = "user" if turn.role == "trainee" else "assistant"
            messages.append({"role": role, "content": turn.text})
        return messages

    def opening_line(self) -> str:
        system = customer_system_prompt(self.scenario)
        opener = [{"role": "user", "content": "[The trainee just approached you in the store. Open the interaction in character.]"}]
        reply = self.chat_client.complete(system, opener)
        self.transcript.turns.append(Turn("customer", reply))
        return reply

    def say(self, trainee_line: str) -> str:
        self.transcript.turns.append(Turn("trainee", trainee_line))
        system = customer_system_prompt(self.scenario)
        reply = self.chat_client.complete(system, self._customer_messages())
        self.transcript.turns.append(Turn("customer", reply))
        return reply

    def hint(self) -> str:
        system = (
            coach_system_prompt(self.scenario)
            + "\n\nThe trainee is stuck right now and asked for help. Suggest 2-3 short, "
            "concrete example lines they could say next, each with a one-line rationale. "
            "Speak to the trainee as their coach, not as the customer."
        )
        prompt = f"Conversation so far:\n{self._transcript_as_text()}\n\nWhat could I say next?"
        return self.chat_client.complete(system, [{"role": "user", "content": prompt}])

    def feedback(self) -> str:
        system = (
            coach_system_prompt(self.scenario)
            + "\n\nGive structured feedback on the conversation so far: what the trainee did "
            "well, specific moments to improve (quote their lines), how they handled "
            "objections and rapport/discovery, and 2-3 concrete things to try next time."
        )
        prompt = f"Conversation:\n{self._transcript_as_text()}\n\nPlease give me feedback."
        result = self.chat_client.complete(system, [{"role": "user", "content": prompt}])
        self.transcript.feedback = result
        return result

    def _transcript_as_text(self) -> str:
        lines = []
        for turn in self.transcript.turns:
            speaker = "Trainee" if turn.role == "trainee" else "Customer"
            lines.append(f"{speaker}: {turn.text}")
        return "\n".join(lines)
