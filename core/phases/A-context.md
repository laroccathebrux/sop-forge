# Phase A — Business context

Loaded once per session, at session start. Goal: fill `state.business` in at most two short
rounds, then exit to Phase B for backlog construction. Phase A writes no SOP files.

## When to enter

- `state.json` does not exist yet → first run `state-manager.py init --language <tag>` with
  the language detected from the user's opening message, then proceed.
- `state.json` exists and `state.business.name` is `null`.

## Procedure

Open with a short, warm greeting in the user's language. One greeting line — no
multi-paragraph introductions. Then ask Round 1 in a single message.

### Round 1 — business basics

Ask three questions in one turn, framed as a small group, not a checklist:

1. Company name and what it does (sector, primary services).
2. Team size (solo, 2–5, 5–20, 20+).
3. Why now? What triggered the desire to document procedures?

Persist the answers immediately:

```
state-manager.py set --json '{
  "business": {
    "name": "...",
    "sector": "...",
    "size": "...",
    "primary_motivation": "..."
  }
}'
```

### Round 2 — sector calibration (only if needed)

Skip Round 2 unless you cannot identify the right sector entry in
`references/sectors.md` from Round 1 alone. If you must ask, ask one targeted follow-up.
Do not grind the user through unnecessary detail — the goal of Phase A is to get out of Phase
A quickly.

## Exit

When `business.name`, `business.sector`, and `business.size` are all populated, exit to
Phase B (Mode 1 — backlog construction) without further user-facing transition text.
