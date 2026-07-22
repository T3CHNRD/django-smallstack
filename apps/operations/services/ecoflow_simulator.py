from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_STATE_KEYS = {
    "grid",
    "battery",
    "soc",
    "input_w",
    "output_w",
    "extra_battery_present",
}


class SimulationProfileError(ValueError):
    """Raised when simulator profile data is invalid."""


@dataclass(frozen=True)
class SimulatedSnapshot:
    profile: str
    model: str
    extra_battery: str
    step: int
    state: dict[str, Any]


class EcoFlowSimulator:
    """Load fixture-backed EcoFlow state profiles and produce mocked transitions."""

    def __init__(self, fixtures_dir: Path | None = None):
        base_dir = Path(__file__).resolve().parent.parent
        self.fixtures_dir = fixtures_dir or base_dir / "fixtures" / "ecoflow_simulator"

    def available_profiles(self) -> list[str]:
        return sorted(path.stem for path in self.fixtures_dir.glob("*.json"))

    def get_snapshot(self, profile: str, step: int = 0) -> SimulatedSnapshot:
        payload = self._load_profile(profile)
        transitions = payload["transitions"]
        normalized_step = step % len(transitions)
        frame = transitions[normalized_step]

        state = {
            "grid": bool(frame["grid"]),
            "battery": str(frame["battery"]),
            "soc": int(frame["soc"]),
            "input_w": int(frame["input_w"]),
            "output_w": int(frame["output_w"]),
            "extra_battery_present": bool(frame["extra_battery_present"]),
        }

        return SimulatedSnapshot(
            profile=payload["profile"],
            model=payload["model"],
            extra_battery=payload["extra_battery"],
            step=normalized_step,
            state=state,
        )

    def build_timeline(self, profile: str, start_step: int = 0, count: int = 5) -> list[SimulatedSnapshot]:
        if count < 1:
            raise SimulationProfileError("count must be at least 1")
        return [self.get_snapshot(profile=profile, step=start_step + offset) for offset in range(count)]

    def _load_profile(self, profile: str) -> dict[str, Any]:
        path = self.fixtures_dir / f"{profile}.json"
        if not path.exists():
            raise SimulationProfileError(f"Unknown simulation profile: {profile}")

        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        self._validate_profile_payload(profile, payload)
        return payload

    def _validate_profile_payload(self, profile: str, payload: dict[str, Any]) -> None:
        for key in ("profile", "model", "extra_battery", "transitions"):
            if key not in payload:
                raise SimulationProfileError(f"Profile '{profile}' missing key: {key}")

        transitions = payload["transitions"]
        if not isinstance(transitions, list) or not transitions:
            raise SimulationProfileError(f"Profile '{profile}' must define at least one transition")

        for index, frame in enumerate(transitions):
            if not isinstance(frame, dict):
                raise SimulationProfileError(
                    f"Profile '{profile}' transition index {index} must be an object"
                )
            missing = REQUIRED_STATE_KEYS.difference(frame.keys())
            if missing:
                missing_str = ", ".join(sorted(missing))
                raise SimulationProfileError(
                    f"Profile '{profile}' transition index {index} missing keys: {missing_str}"
                )
