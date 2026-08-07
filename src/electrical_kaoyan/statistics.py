from __future__ import annotations

from math import fsum, sqrt
from statistics import median


def _quantile(sorted_values: list[float], probability: float) -> float:
    position = (len(sorted_values) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    fraction = position - lower
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * fraction


def score_distribution(values: list[float | int | None]) -> dict[str, float | int] | None:
    clean = sorted(float(value) for value in values if value is not None)
    if not clean:
        return None
    mean = fsum(clean) / len(clean)
    variance = fsum((value - mean) ** 2 for value in clean) / len(clean)
    return {
        "minimum": clean[0],
        "q1": _quantile(clean, 0.25),
        "median": median(clean),
        "mean": mean,
        "q3": _quantile(clean, 0.75),
        "maximum": clean[-1],
        "standard_deviation": sqrt(variance),
        "sample_size": len(clean),
    }
