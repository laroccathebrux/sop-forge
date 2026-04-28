# Phase E — Review and transition

Loaded after Phase D has written a SOP file. Phase E shows a summary, handles user
corrections, marks the backlog entry complete, and decides whether to loop back to Phase B
or exit to Phase F.

Phase E **never pastes the generated file body into chat**. Always summary-only.

## Step 1 — Summary

Read the just-written file from disk if you need to verify content. Then emit a compact
summary in the user's language. Translate the example phrasing:

> "POP-01 — Client check-in is saved.
>
> - **X steps** in the procedure
> - **Owner:** receptionist
> - **Watch for:** wrong patient identification, double-booked slots
>
> Anything to fix before we move on?"

Pull the numbers and bullets from `state.current_pop_notes` directly — do not re-read the
SOP file unless the user explicitly asks about something that is only in the file body.

## Step 2 — Corrections

If the user requests changes:

1. Edit the file in place. Do not rewrite from scratch.
2. Update `state.current_pop_notes` if the change affects structured fields (steps, risks,
   etc.) so the next run sees consistent state.
3. Tell the user only what changed (one or two sentences). Do not paste the full file.

If the user approves, proceed to Step 3.

## Step 3 — Mark complete and clear notes

```
state-manager.py update-pop POP-NN --status completed
state-manager.py clear-notes
```

## Step 4 — Transition

Show the backlog status as a compact list (translated headings):

```
✅ POP-01 — Client check-in              [done]
⏳ POP-02 — Phone scheduling             [next]
○  POP-03 — Opening procedure
○  POP-04 — ...
```

Then ask one of:

- "Continue with POP-02?" — if pending items remain.
- "Backlog is empty. Want me to wrap up the session?" — if none remain.

Decision tree:

- User says continue → exit to Phase B (Mode 2) with the next pending entry.
- User picks a different POP → set its status to `in_progress`, exit to Phase B (Mode 2).
- User adds a new POP → use `add-pop` first, then continue as above.
- User wants to stop or backlog is empty → exit to Phase F.
