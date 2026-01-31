from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .db import connect

@dataclass(frozen=True)
class HistoryItem:
    reviewed_at: int
    lc_num: int
    title: str
    grade: str
    next_due_at: Optional[int]
    note: Optional[str]

def fetch_history(db_path: Path, n: int = 20, include_seed: bool = False) -> List[HistoryItem]:
    conn = connect(db_path)

    where = "" if include_seed else "WHERE l.grade != 'seed'"
    rows = conn.execute(
        f"""
        SELECT l.reviewed_at, l.lc_num,
               COALESCE(p.title, '') AS title,
               l.grade, l.next_due_at, l.note
        FROM review_logs l
        LEFT JOIN problems p ON p.lc_num = l.lc_num
        {where}
        ORDER BY l.reviewed_at DESC, l.id DESC
        LIMIT ?;
        """,
        (n,),
    ).fetchall()

    conn.close()
    return [
        HistoryItem(
            reviewed_at=int(r["reviewed_at"]),
            lc_num=int(r["lc_num"]),
            title=str(r["title"]),
            grade=str(r["grade"]),
            next_due_at=(int(r["next_due_at"]) if r["next_due_at"] is not None else None),
            note=(str(r["note"]) if r["note"] is not None else None),
        )
        for r in rows
    ]

