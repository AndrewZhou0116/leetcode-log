# LeetCode Log CLI (Plan Cursor + SRS)

A lightweight CLI to run a **plan-ordered** LeetCode workflow with an **Anki-ish spaced repetition scheduler** (SQLite-backed).

## Core principles
- **Plan is authoritative**: NEW always follows `plan_order` imported from `plan.txt`.
- **Done never disappears**: `done` moves NEW → SRS (REVIEW). Move the cursor back and a problem can become NEW again.
- **Cursor only affects NEW**: REVIEW is driven purely by `due_at` (independent of cursor).
- **Reproducible**: explicit SQLite schema + import/reset utilities.

## Commands

### Daily workflow
- `lc show` — show today’s **NEW + REVIEW**
- `lc open` — open LeetCode filtered by current NEW target
- `lc done <lc_num> <grade> [--note "..."]` — record review + schedule next due  
  Grades: `again | hard | good | easy`
- `lc note <lc_num> "..."` — write/overwrite note
- `lc <lc_num> note` — view note
- `lc history` — review logs
- `lc stats` — cursor + counts + due load + activity

### Plan / DB utilities
- `lc init` — create DB + schema
- `lc import plan.txt` — import plan order from `plan.txt`
- `lc reset` — rebuild DB (optionally backup)
- `lc cursor set <lc_num>` — set NEW start point by problem id
- `lc mark-done-before <lc_num>` — add all prior problems into SRS and mark them due (bootstrap)

Data tables: `problems`, `reviews`, `review_logs`, `meta`.

## Install

```bash
# Option A: editable install (recommended)
git clone <YOUR_REPO_URL>
cd <repo>
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .

# Option B: pipx (global, isolated)
# (run this from inside the repo directory)
pipx install -e .

### Quik start

lc init
lc import plan.txt

lc show
lc open
lc done 1011 good --note "binary search on answer space"
lc show


###Database location

You can choose where the SQLite DB lives:

Override with env var:

export LCSRS_DB=/path/to/lcs.db


Or per command:

lc show --db /path/to/lcs.db

Scheduling model (day granularity)

Each review updates: interval_days, ease, reps, lapses, easy_streak, due_at.

again: reset interval (high frequency), decrease ease, lapses++

hard: slow growth, decrease ease

good: interval grows by * ease

easy: faster growth (* ease * 1.3), increase ease; 3× easy ⇒ retired

REVIEW is sorted by due_at (earliest first). Cursor never affects REVIEW.

plan.txt format

Example:

Phase 0: Arrays / Strings
1 Two Sum
26 Remove Duplicates from Sorted Array
...


Only lines starting with a number are treated as problems; headers are ignored.
