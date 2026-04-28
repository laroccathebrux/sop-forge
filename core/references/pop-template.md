# SOP template

Canonical structure for the `.md` file emitted by Phase D. Fill the bracketed placeholders
with values from `state.current_pop_notes` (translated to `state.language` at render time —
notes themselves are stored in English).

Translate all headings to the user's language at render time. Keep the same heading order
and the same YAML frontmatter keys (frontmatter values may be localized except for `id`,
`area`, `target_category`, and `schema_version`, which stay in their canonical form).

Where the user did not provide a value, write `[TBD]`. Do not invent content.

---

```markdown
---
id: <POP-NN>
title: <localized title>
area: <AREA_NAME>
target_category: <HUMAN_TRIGGERED | TIME_OR_EVENT_TRIGGERED | AMBIGUOUS>
generated_at: <ISO-8601 timestamp>
schema_version: 1
---

# <localized title>

## Purpose

<One or two sentences explaining what this procedure is for. Derive from the notes if the
user did not state it explicitly.>

## Trigger

<Single sentence describing what initiates the procedure — from
`current_pop_notes.trigger`.>

## Owner

<Role responsible for executing — from `current_pop_notes.owner`. Mention the backup role
on the same line if the user identified one.>

## Resources

<Bulleted list of products, equipment, systems, or forms used — from
`current_pop_notes.resources`. If the user did not specify, write `[TBD]`.>

## Procedure

<Numbered list of steps in imperative voice — from `current_pop_notes.steps`. One step per
item. Use `[TBD]` inline for sub-details the user did not provide.>

## Risks

<Bulleted list of common errors, edge cases, or hard constraints — from
`current_pop_notes.risks`. `[TBD]` if missing.>

## Quality criterion

<Single sentence describing how to know the procedure was executed well. `[TBD]` if the
user did not specify.>

## Exceptions

<Bulleted list of off-path scenarios (cancellations, missing inventory, off-hours, etc.).
`[TBD]` if missing.>

## Change log

- <YYYY-MM-DD> — initial version
```
