from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

SECONDS_PER_DAY = 86400

@dataclass(frozen=True)
class ReviewState:
    due_at: int
    interval_days: float
    ease: float
    reps: int
    lapses: int
    easy_streak: int
    last_grade: str
    status: str  # active|retired

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def next_state(prev: Optional[ReviewState], grade: str, now: int) -> ReviewState:
    """
    Anki-ish day-granularity scheduler + 3x easy => retired.
    grade in: again|hard|good|easy
    """
    grade = grade.lower().strip()
    if grade not in {"again", "hard", "good", "easy"}:
        raise ValueError("grade must be one of: again, hard, good, easy")

    if prev is None:
        # First time entering SRS from NEW
        ease = 2.50
        reps = 0
        lapses = 0
        easy_streak = 0
        if grade == "again":
            interval = 1.0
            ease = clamp(ease - 0.20, 1.30, 3.00)
            lapses += 1
        elif grade == "hard":
            interval = 2.0
            ease = clamp(ease - 0.15, 1.30, 3.00)
        elif grade == "good":
            interval = 3.0
        else:  # easy
            interval = 5.0
            ease = clamp(ease + 0.15, 1.30, 3.00)
            easy_streak = 1

        status = "active"
        if easy_streak >= 3:
            status = "retired"
        due_at = now + int(round(interval) * SECONDS_PER_DAY)

        return ReviewState(
            due_at=due_at,
            interval_days=interval,
            ease=ease,
            reps=reps + (1 if grade != "again" else 0),
            lapses=lapses,
            easy_streak=easy_streak,
            last_grade=grade,
            status=status,
        )

    # Existing review
    ease = prev.ease
    interval = prev.interval_days
    reps = prev.reps
    lapses = prev.lapses
    easy_streak = prev.easy_streak

    if grade == "again":
        ease = clamp(ease - 0.20, 1.30, 3.00)
        interval = 1.0
        lapses += 1
        easy_streak = 0
    elif grade == "hard":
        ease = clamp(ease - 0.15, 1.30, 3.00)
        interval = max(2.0, interval * 1.20)
        easy_streak = 0
        reps += 1
    elif grade == "good":
        interval = max(3.0, interval * ease)
        easy_streak = 0
        reps += 1
    else:  # easy
        ease = clamp(ease + 0.15, 1.30, 3.00)
        interval = max(5.0, interval * ease * 1.30)
        easy_streak += 1
        reps += 1

    status = "retired" if easy_streak >= 3 else "active"
    due_at = now + int(round(interval) * SECONDS_PER_DAY)

    return ReviewState(
        due_at=due_at,
        interval_days=interval,
        ease=ease,
        reps=reps,
        lapses=lapses,
        easy_streak=easy_streak,
        last_grade=grade,
        status=status,
    )

