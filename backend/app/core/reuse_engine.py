from __future__ import annotations

from typing import Any, Dict, Tuple

from app.core.pattern_registry import PatternRegistry


class ReuseEngine:
    """
    Phase-3 reuse engine.

    Checks:
    1. exact reuse via step_signature
    2. invariant reuse via invariant_signature
    3. partial similarity reuse via normalized task structure
    4. family reuse via family_hint
    """

    def __init__(self, registry: PatternRegistry) -> None:
        self.registry = registry

    def check_reuse(
        self,
        *,
        step_signature: str,
        invariant_signature: str,
        family_hint: str,
        normalized_task: Dict[str, Any],
    ) -> Dict[str, Any]:
        exact = self.registry.get_exact(step_signature)
        if exact:
            self.registry.record_hit(step_signature, "exact")
            return {
                "match_type": "exact",
                "matched_pattern": exact,
                "reason": "Exact step signature match found.",
                "confidence": 0.99,
            }

        partial = self.registry.get_by_invariant(invariant_signature)
        if partial:
            self.registry.record_hit(partial["step_signature"], "partial")
            return {
                "match_type": "partial",
                "matched_pattern": partial,
                "reason": "Invariant signature match found.",
                "confidence": 0.88,
            }

        best_match, best_score = self._find_best_partial_match(
            normalized_task=normalized_task,
            family_hint=family_hint,
        )
        if best_match and best_score >= 0.60:
            self.registry.record_hit(best_match["step_signature"], "partial")
            return {
                "match_type": "partial",
                "matched_pattern": best_match,
                "reason": f"Structural similarity match found ({best_score:.2f}).",
                "confidence": round(best_score, 2),
            }

        family = self.registry.get_by_family(family_hint)
        if family:
            self.registry.record_hit(family["step_signature"], "family")
            return {
                "match_type": "family",
                "matched_pattern": family,
                "reason": "Family-level reusable pattern found.",
                "confidence": 0.58,
            }

        return {
            "match_type": "none",
            "matched_pattern": None,
            "reason": "No reusable pattern found. Execute fresh.",
            "confidence": 0.35,
        }

    def _find_best_partial_match(
        self,
        *,
        normalized_task: Dict[str, Any],
        family_hint: str,
    ) -> Tuple[Dict[str, Any] | None, float]:
        state = self.registry.get_state()
        patterns = state.get("patterns", {})

        current_step = normalized_task.get("canonical_step", "unknown")
        current_features = normalized_task.get("normalized_features", {}) or {}
        current_feature_keys = set(current_features.keys())
        current_family = (family_hint or "").lower()

        best_match = None
        best_score = 0.0

        for pattern in patterns.values():
            stored_task = pattern.get("normalized_task", {}) or {}
            stored_step = stored_task.get("canonical_step", "unknown")
            stored_features = stored_task.get("normalized_features", {}) or {}
            stored_feature_keys = set(stored_features.keys())
            stored_family = (pattern.get("family_hint") or "").lower()

            step_score = 1.0 if stored_step == current_step else 0.0
            family_score = 1.0 if stored_family == current_family and current_family else 0.0
            feature_score = self._jaccard(current_feature_keys, stored_feature_keys)

            total_score = (
                (0.45 * step_score) +
                (0.25 * family_score) +
                (0.30 * feature_score)
            )

            if total_score > best_score:
                best_score = total_score
                best_match = pattern

        return best_match, best_score

    def _jaccard(self, left: set[str], right: set[str]) -> float:
        union = left | right
        if not union:
            return 1.0
        intersection = left & right
        return len(intersection) / len(union)