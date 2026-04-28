# Phase B — Backlog construction and per-SOP brainstorm

Phase B has two modes. Pick the mode from state, do not ask the user which one.

- **Mode 1 — Backlog construction:** `state.backlog` is empty and `state.business.name` is
  set. Build the initial list from sectoral hints, persist, and re-enter Phase B in Mode 2.
- **Mode 2 — Per-SOP brainstorm:** `state.current_pop_notes` is `null` and at least one
  backlog entry has `status == "pending"`. Pick the next pending entry, mark it
  `in_progress`, populate `current_pop_notes` through brief conversation, then exit to
  Phase D.

---

## Mode 1 — Backlog construction

Load `core/references/sectors.md` and find the entry matching `state.business.sector`.
If no exact match exists, pick the closest sibling and proceed; do not ask the user for
disambiguation here.

Present a candidate backlog grouped by area. Translate the example phrasing below to the
user's language at runtime:

> "Based on what you told me, I suggest starting with these POPs:
>
> **Area: Front-of-house**
> - Opening procedure
> - Client check-in
> - Phone scheduling
>
> **Area: Service delivery**
> - ...
>
> Does this list look right? Anything to add, remove, or rename?"

After the user confirms, persist each entry:

```
state-manager.py add-pop --area FRONT_OF_HOUSE \
  --name client-checkin --display-name "Check-in do cliente"
```

- `area` — ALL-CAPS English, snake_case for multi-word areas.
- `name` — English kebab-case identifier; this is what appears in generated file paths.
- `display_name` — user-language label for chat output (optional but recommended).
- Do **not** infer `target_category` here — that happens silently during Mode 2.

Once the backlog is persisted, ask which POP to start with (or recommend the simplest /
most-urgent), then re-enter Phase B in Mode 2.

---

## Mode 2 — Per-SOP brainstorm

Pick the next pending entry from `state.backlog`. Mark it in progress:

```
state-manager.py update-pop POP-NN --status in_progress
```

Load `core/references/pop-template.md` so you know the target output shape.

Announce which POP you are working on (one short sentence, user's language). Then ask in
two thematic rounds — never as a single long list.

### Round 1 — flow

1. **Trigger** — what starts this procedure? (walk-in, request, time, threshold, ...)
2. **Owner** — which role executes? Is there a backup?
3. **Steps** — what happens, in order? Ask the user to describe the flow in their own words.

### Round 2 — depth (legacy Phase C folded in)

Only ask what is still missing after Round 1:

1. **Risks** — common errors, hard edge cases, what must never happen.
2. **Resources** — products, equipment, systems, forms used.
3. **Estimated duration** and **quality criterion** — only if relevant to this SOP type.
4. **Exceptions** — cancellations, missing inventory, off-hours, etc.

If the user does not know an answer, write `[TBD]` and continue. Do not block on missing
detail.

### Silent target classification

While listening, classify the SOP. The categories and their meaning are defined in
`core/SKILL.md` under "Target inference" — do not duplicate the rules here. Do **not**
mention the categories or any framework name to the user; surface confirmation belongs to
Phase D.

### Exit

Persist the notes and exit to Phase D:

```
state-manager.py set-notes --json '{
  "pop_id": "POP-NN",
  "trigger": "...",
  "owner": "...",
  "steps": ["..."],
  "risks": ["..."],
  "resources": ["..."],
  "target_category": "HUMAN_TRIGGERED"
}'
```

All values inside the notes are stored in English (translate at write-time). The user-
language SOP body is rendered later, in Phase D, from these notes.
