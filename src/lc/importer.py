from __future__ import annotations

from pathlib import Path
from typing import Tuple

from .db import connect, tx
from .plan_parser import parse_plan_file

UPSERT_SQL = """
INSERT INTO problems(lc_num, title, phase, plan_order, is_optional)
VALUES(?,?,?,?,?)
ON CONFLICT(lc_num) DO UPDATE SET
  title=excluded.title,
  phase=excluded.phase,
  plan_order=excluded.plan_order,
  is_optional=excluded.is_optional;
"""

def import_plan(db_path: Path, plan_path: Path) -> Tuple[int, int]:
    items = parse_plan_file(plan_path)

    conn = connect(db_path)
    with tx(conn):
        for it in items:
            conn.execute(UPSERT_SQL, (it.lc_num, it.title, it.phase, it.plan_order, it.is_optional))

        # 如果 cursor 还在 1，但 plan_order 不是从 1 开始（极少），可以修正；
        # 或者 cursor 超过最大 plan_order，则夹回范围内
        max_order = conn.execute("SELECT MAX(plan_order) AS m FROM problems;").fetchone()["m"] or 1
        cur = conn.execute("SELECT value FROM meta WHERE key='cursor_plan_order';").fetchone()
        if cur is None:
            conn.execute("INSERT INTO meta(key,value) VALUES('cursor_plan_order','1');")
        else:
            cur_val = int(cur["value"])
            if cur_val < 1:
                conn.execute("UPDATE meta SET value='1' WHERE key='cursor_plan_order';")
            elif cur_val > max_order + 1:
                conn.execute("UPDATE meta SET value=? WHERE key='cursor_plan_order';", (str(max_order + 1),))

    conn.close()
    return (len(items), items[-1].plan_order if items else 0)
