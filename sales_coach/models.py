from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Scenario:
    name: str
    product_or_service: str
    customer_persona: str
    personality_traits: list = field(default_factory=list)
    objections_focus: list = field(default_factory=list)
    difficulty: str = "medium"
    goal: str = ""
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "product_or_service": self.product_or_service,
            "customer_persona": self.customer_persona,
            "personality_traits": self.personality_traits,
            "objections_focus": self.objections_focus,
            "difficulty": self.difficulty,
            "goal": self.goal,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Scenario":
        return cls(
            name=data["name"],
            product_or_service=data.get("product_or_service", ""),
            customer_persona=data.get("customer_persona", ""),
            personality_traits=list(data.get("personality_traits", [])),
            objections_focus=list(data.get("objections_focus", [])),
            difficulty=data.get("difficulty", "medium"),
            goal=data.get("goal", ""),
            notes=data.get("notes", ""),
        )


@dataclass
class Turn:
    role: str  # "trainee" or "customer"
    text: str


@dataclass
class Transcript:
    scenario: Scenario
    turns: list = field(default_factory=list)
    feedback: Optional[str] = None
