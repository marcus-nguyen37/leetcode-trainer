# leetcode-trainer
Dashboard for LeetCode practice meant to optimise learning.

## Design notes
Problems stored using their official LeetCode numeric **ID**.

All database operations (and CLI commands) expect this ID when referring to a problem.

## CLI Usage Examples

```bash
# add a problem to the local cache
python main.py add_problem 1 "Two Sum" Easy "Array,Hash Table"

# log an attempt for problem w/ ID 1
python main.py log 1 2026-02-19 30 4 1
```
