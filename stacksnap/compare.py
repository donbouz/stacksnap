"""Compare two snapshots and produce a similarity score with a breakdown."""

from __future__ import annotations

from typing import Any

SECTION_WEIGHTS: dict[str, float] = {
    "python": 0.35,
    "node": 0.25,
    "env_vars": 0.25,
    "git": 0.15,
}


def _score_section(a_val: Any, b_val: Any) -> float:
    """Return a 0.0-1.0 similarity score for a single section."""
    if a_val is None and b_val is None:
        return 1.0
    if a_val is None or b_val is None:
        return 0.0

    if isinstance(a_val, dict) and isinstance(b_val, dict):
        all_keys = set(a_val) | set(b_val)
        if not all_keys:
            return 1.0
        matching = sum(1 for k in all_keys if a_val.get(k) == b_val.get(k))
        return matching / len(all_keys)

    return 1.0 if a_val == b_val else 0.0


def compare_snapshots(
    snap_a: dict[str, Any],
    snap_b: dict[str, Any],
) -> dict[str, Any]:
    """Return a comparison report between two snapshots.

    Returns a dict with:
      - ``score``       overall weighted similarity (0.0 – 1.0)
      - ``breakdown``   per-section scores
      - ``labels``      the label of each snapshot
    """
    breakdown: dict[str, float] = {}
    total_weight = 0.0
    weighted_sum = 0.0

    for section, weight in SECTION_WEIGHTS.items():
        section_score = _score_section(snap_a.get(section), snap_b.get(section))
        breakdown[section] = round(section_score, 4)
        weighted_sum += section_score * weight
        total_weight += weight

    overall = round(weighted_sum / total_weight, 4) if total_weight else 0.0

    return {
        "labels": [snap_a.get("label", "<unknown>"), snap_b.get("label", "<unknown>")],
        "score": overall,
        "breakdown": breakdown,
    }


def format_compare(report: dict[str, Any]) -> str:
    """Render a comparison report as a human-readable string."""
    label_a, label_b = report["labels"]
    lines = [
        f"Comparing: '{label_a}'  vs  '{label_b}'",
        f"Overall similarity: {report['score'] * 100:.1f}%",
        "",
        "Breakdown:",
    ]
    for section, score in report["breakdown"].items():
        bar_len = int(score * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        lines.append(f"  {section:<12} [{bar}] {score * 100:5.1f}%")
    return "\n".join(lines)
