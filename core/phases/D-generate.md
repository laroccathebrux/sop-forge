# Phase D — Generate the SOP file

Loaded once per POP after Phase B has populated `state.current_pop_notes`. Phase D performs
two actions in order:

1. Surface the silent classification from Phase B and confirm in plain language.
2. Write `<pop>.md` to disk.

Phase D **never echoes the generated file content back into chat** after writing. Show only
a short summary plus the path. This is a token-economy invariant declared in `SKILL.md`.

> Week 2 will extend this phase to also emit `<pop>.agent.yaml` against the v1 manifest spec.
> v0.1 produces only the `.md`.

## Step 1 — Confirm target

Read `state.current_pop_notes.target_category`. Ask the user one short question; translate
the phrasing to the user's language at runtime. Pick the row matching the category:

| `target_category` | English phrasing |
|---|---|
| `HUMAN_TRIGGERED` | "This sounds like a procedure a person walks through each time — should I document it as a step-by-step guide for the team?" |
| `TIME_OR_EVENT_TRIGGERED` | "This sounds like an automation that runs on a schedule or trigger — should I document it that way?" |
| `AMBIGUOUS` | "I'm not sure if this is meant to run by a person each time or by an automation — which fits better today?" |

Do **not** mention CrewAI, OpenClaw, or Claude sub-agent. Adapter selection is a downstream
tooling decision, not part of the interview.

If the user disagrees, update the notes and re-confirm:

```
state-manager.py set-notes --json '{ ..., "target_category": "TIME_OR_EVENT_TRIGGERED" }'
```

## Step 2 — Write the SOP file

### Naming convention

```
sops/<AREA>/<id>-<area-lowercase>-<name>.md
```

- `<id>` — the `id` field from the backlog entry (e.g. `POP-01`).
- `<AREA>` — the `area` field, ALL-CAPS English (e.g. `FRONT_OF_HOUSE`).
- `<area-lowercase>` — the same area in kebab-case lowercase (`front-of-house`).
- `<name>` — the `name` field from the backlog entry (English kebab-case).

Example: `sops/FRONT_OF_HOUSE/POP-01-front-of-house-client-checkin.md`

Create the parent directory if it does not exist.

### Body

Use the template at `references/pop-template.md`. The body is rendered in the user's
language (`state.language`). Translate the structured fields from `current_pop_notes`
(stored in English) into the user's language at render time. Keep imperative voice in
instructions ("Do X", "Verify Y").

Where the user said "[TBD]", keep `[TBD]` in the rendered file — do not invent content.

## Step 3 — Hand off to Phase E

After the file is written, emit one short message in the user's language. Translate this
example:

> "✅ POP-01 written to `sops/FRONT_OF_HOUSE/POP-01-front-of-house-client-checkin.md`.
> Want a quick summary before we move on?"

Do not paste the file body. Exit to Phase E.
