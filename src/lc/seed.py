from __future__ import annotations

import time
from pathlib import Path

from .db import connect, tx, set_meta

def _plan_order_of(conn, lc_num: int) -> int:
    row = conn.execute("SELECT plan_order FROM problems WHERE lc_num=?;", (lc_num,)).fetchone()
    if not row:
        raise ValueError(f"lc_num {lc_num} not found in problems (did you import plan.txt?)")
    return int(row["plan_order"])

def cursor_set(db_path: Path, lc_num: int) -> int:
    conn = connect(db_path)
    with tx(conn):
        po = _plan_order_of(conn, lc_num)
        set_meta(conn, "cursor_plan_order", str(po))
    conn.close()
    return po

def mark_done_before(db_path: Path, lc_num: int, force: bool = False) -> int:
    """
    For all problems with plan_order < plan_order(lc_num):
    - ensure they exist in reviews
    - set due_at <= now so they show up in REVIEW
    If force=True, also force existing reviews to due now.
    Returns number of newly seeded problems.
    """
    now = int(time.time())
    due_now = now - 1

    conn = connect(db_path)
    with tx(conn):
        target_po = _plan_order_of(conn, lc_num)

        # seed missing reviews rows
        rows = conn.execute(
            """
            SELECT p.lc_num
            FROM problems p
            LEFT JOIN reviews r ON r.lc_num=p.lc_num
            WHERE p.plan_order < ?
              AND r.lc_num IS NULL;
            """,
            (target_po,),
        ).fetchall()

        for r in rows:
            n = int(r["lc_num"])
            conn.execute(
                """
                INSERT INTO reviews(lc_num, due_at, interval_days, ease, reps, lapses, easy_streak, last_grade, status, updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?);
                """,
                (n, due_now, 1.0, 2.50, 0, 0, 0, "seed", "active", now),
            )
            conn.execute(
                """
                INSERT INTO review_logs(
                  lc_num, reviewed_at, grade,
                  prev_due_at, next_due_at,
                  prev_intvl, next_intvl,
                  prev_ease, next_ease,
                  note
                ) VALUES(?,?,?,?,?,?,?,?,?,?);
                """,
                (n, now, "seed", None, due_now, None, 1.0, None, 2.50, "seeded by mark-done-before"),
            )

        if force:
            conn.execute(
                """
                UPDATE reviews
                SET due_at=?, status='active', updated_at=?
                WHERE lc_num IN (SELECT lc_num FROM problems WHERE plan_order < ?);
                """,
                (due_now, now, target_po),
            )

        # keep NEW aligned
        set_meta(conn, "cursor_plan_order", str(target_po))

    conn.close()
    return len(rows)

