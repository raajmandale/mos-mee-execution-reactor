from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "pattern_graph.json"


class PatternRegistry:
    """
    Phase-2 persistent pattern registry.

    Stores:
    - exact patterns keyed by step_signature
    - invariant index for partial reuse
    - family index for family-level reuse
    - graph payloads for later execution layers
    - reuse history counters
    - frontend-facing run history
    """

    def __init__(self, data_path: Optional[Path] = None) -> None:
        self.data_path = data_path or DEFAULT_DATA_PATH
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self._state = self._load()

    def _empty_state(self) -> Dict[str, Any]:
        return {
            "patterns": {},
            "invariant_index": {},
            "family_index": {},
            "reuse_history": {},
            "runs": [],
        }

    def _load(self) -> Dict[str, Any]:
        if not self.data_path.exists():
            state = self._empty_state()
            self._save(state)
            return state

        try:
            with self.data_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = self._empty_state()
            self._save(data)

        for key, default in self._empty_state().items():
            data.setdefault(key, default)

        return data

    def _save(self, state: Optional[Dict[str, Any]] = None) -> None:
        payload = state if state is not None else self._state
        with self.data_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    def get_state(self) -> Dict[str, Any]:
        return self._state

    def get_runs(self) -> List[Dict[str, Any]]:
        runs = self._state.get("runs", [])
        return list(runs)

    def get_exact(self, step_signature: str) -> Optional[Dict[str, Any]]:
        return self._state["patterns"].get(step_signature)

    def get_by_invariant(self, invariant_signature: str) -> Optional[Dict[str, Any]]:
        step_signature = self._state["invariant_index"].get(invariant_signature)
        if not step_signature:
            return None
        return self._state["patterns"].get(step_signature)

    def get_by_family(self, family_hint: str) -> Optional[Dict[str, Any]]:
        signatures = self._state["family_index"].get(family_hint, [])
        if not signatures:
            return None
        latest_signature = signatures[-1]
        return self._state["patterns"].get(latest_signature)

    def store_pattern(
        self,
        *,
        step_signature: str,
        invariant_signature: str,
        family_hint: str,
        normalized_task: Dict[str, Any],
        graph: Dict[str, Any],
    ) -> Dict[str, Any]:
        pattern_record = {
            "step_signature": step_signature,
            "invariant_signature": invariant_signature,
            "family_hint": family_hint,
            "normalized_task": normalized_task,
            "graph": graph,
        }

        self._state["patterns"][step_signature] = pattern_record
        self._state["invariant_index"][invariant_signature] = step_signature

        family_bucket = self._state["family_index"].setdefault(family_hint, [])
        if step_signature not in family_bucket:
            family_bucket.append(step_signature)

        self._state["reuse_history"].setdefault(
            step_signature,
            {
                "exact_hits": 0,
                "partial_hits": 0,
                "family_hits": 0,
                "fresh_runs": 0,
            },
        )
        self._state["reuse_history"][step_signature]["fresh_runs"] += 1

        self._save()
        return pattern_record

    def record_hit(self, step_signature: str, match_type: str) -> None:
        history = self._state["reuse_history"].setdefault(
            step_signature,
            {
                "exact_hits": 0,
                "partial_hits": 0,
                "family_hits": 0,
                "fresh_runs": 0,
            },
        )

        if match_type == "exact":
            history["exact_hits"] += 1
        elif match_type == "partial":
            history["partial_hits"] += 1
        elif match_type == "family":
            history["family_hits"] += 1

        self._save()

    def append_run(self, run_record: Dict[str, Any]) -> None:
        runs = self._state.setdefault("runs", [])
        runs.insert(0, run_record)
        self._save()

    def reset_all(self) -> None:
        self._state = self._empty_state()
        self._save()