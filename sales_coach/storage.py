from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Union

from .models import Scenario, Transcript


class ScenarioStore:
    def __init__(self, directory: Union[Path, str]):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        safe = name.strip().lower().replace(" ", "_")
        return self.directory / f"{safe}.json"

    def save(self, scenario: Scenario) -> Path:
        path = self._path(scenario.name)
        path.write_text(json.dumps(scenario.to_dict(), indent=2))
        return path

    def load(self, name: str) -> Scenario:
        path = self._path(name)
        if not path.exists():
            raise FileNotFoundError(f"No scenario named '{name}' in {self.directory}")
        return Scenario.from_dict(json.loads(path.read_text()))

    def list(self) -> List[str]:
        return sorted(p.stem for p in self.directory.glob("*.json"))


def save_transcript(transcript: Transcript, directory: Union[Path, str]) -> Path:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    safe_name = transcript.scenario.name.strip().lower().replace(" ", "_")
    path = directory / f"{stamp}-{safe_name}.json"
    data = {
        "scenario": transcript.scenario.to_dict(),
        "turns": [{"role": t.role, "text": t.text} for t in transcript.turns],
        "feedback": transcript.feedback,
    }
    path.write_text(json.dumps(data, indent=2))
    return path
