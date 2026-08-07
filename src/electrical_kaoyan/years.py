from __future__ import annotations

import re

from .models import AdmissionCycle


def cycle_from_admission_year(admission_year: int) -> AdmissionCycle:
    return AdmissionCycle(admission_year=admission_year, exam_year=admission_year - 1)


def infer_admission_year(text: str) -> int | None:
    """Infer only from explicit cohort wording, never from publication time alone."""
    patterns = (
        r"(?P<year>20\d{2})\s*年(?:硕士研究生)?(?:招生|入学|录取)",
        r"(?P<year>20\d{2})\s*(?:级|届)硕士",
        r"(?P<year>20\d{2})\s*考研",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group("year"))
    return None
