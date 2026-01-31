from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

PHASE_RE = re.compile(r"^\s*Phase\s*\d+\s*[:：]\s*(.+?)\s*$")
PROBLEM_RE = re.compile(r"^\s*(?P<opt>【\+】)?\s*(?P<num>\d+)\s+(?P<title>.+?)\s*$")

@dataclass(frozen=True)
class PlanItem:
    lc_num: int
    title: str
    phase: str
    plan_order: int
    is_optional: int  # 0/1

def parse_plan_lines(lines: Iterable[str]) -> list[PlanItem]:
    phase = "Uncategorized"
    order = 0
    items: list[PlanItem] = []

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        m_phase = PHASE_RE.match(line)
        if m_phase:
            phase = m_phase.group(1)
            continue

        m_prob = PROBLEM_RE.match(line)
        if not m_prob:
            # 允许出现解释行/备注行：直接跳过
            # （你 plan 里有很多中文分类标题，这样不会炸）
            continue

        order += 1
        is_optional = 1 if m_prob.group("opt") else 0
        lc_num = int(m_prob.group("num"))
        title = m_prob.group("title").strip()

        items.append(PlanItem(lc_num, title, phase, order, is_optional))

    # 基本健壮性：lc_num 不能重复
    seen = set()
    dup = [x.lc_num for x in items if (x.lc_num in seen) or seen.add(x.lc_num)]
    if dup:
        raise ValueError(f"duplicate lc_num in plan: {sorted(set(dup))}")

    return items

def parse_plan_file(path: Path) -> list[PlanItem]:
    return parse_plan_lines(path.read_text(encoding="utf-8").splitlines())
