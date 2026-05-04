# backend/app/core/decision_engine.py

from typing import Dict, Any


class DecisionEngine:

    def __init__(self):
        pass

    def evaluate(self, step_name: str, context: Dict, reuse_available: bool) -> Dict:
        """
        Core decision logic:
        Decide whether to reuse or recompute + explain WHY
        """

        # --- Base scoring ---
        cost_recompute = context.get("cost", 1.0)
        reuse_score = context.get("reuse_score", 0.0)  # 0 → 1
        similarity = context.get("similarity", 0.0)    # 0 → 1

        # --- Decision Logic ---
        if reuse_available and similarity > 0.85:
            action = "reused"
            reason = "High similarity with existing pattern"
            confidence = round(similarity, 2)
            cost_saved = round(cost_recompute * similarity, 3)

        elif reuse_available and similarity > 0.60:
            action = "partial_reuse"
            reason = "Moderate similarity, partial reuse applied"
            confidence = round(similarity * 0.8, 2)
            cost_saved = round(cost_recompute * (similarity * 0.6), 3)

        else:
            action = "recomputed"
            reason = "Low similarity or no reusable pattern"
            confidence = 0.5
            cost_saved = 0.0

        return {
            "step": step_name,
            "action": action,
            "reason": reason,
            "confidence": confidence,
            "cost_saved": cost_saved,
            "cost_full": cost_recompute
        }