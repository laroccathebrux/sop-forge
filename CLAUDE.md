# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

`sop-forge` is the public open-source rewrite of a private Claude skill called `pop-generator`. It conducts a conversational interview about a business's procedures and produces three classes of artifact:

1. Human-readable SOPs (`.md`)
2. Universal agent manifests (`.agent.yaml`) — framework-agnostic
3. Framework-specific code via adapters (CrewAI, Claude sub-agents) and integrations (OpenClaw)

The technical reason this project exists is **token economy**: the original skill caused a real rate-limit incident. Every architectural decision flows from that.

## Status and cadence

The work follows a 4-week plan kept locally at `.private/plan/sop-forge-4-week-plan.md` (gitignored — not in the public repo). On the maintainer's machine, read it before acting on anything non-trivial. On a fresh clone without `.private/`, this CLAUDE.md and the README cover the essentials.

- Week 1: Refactor the legacy skill into modular, lazy-loaded core. State manager + token budget tracker. One real-world test session.
- Week 2: Manifest spec v1 + CrewAI adapter (flagship).
- Week 3: OpenClaw integration + Claude sub-agent adapter.
- Week 4: Public launch (README in EN/PT, token-economy article, GitHub Actions, posts).

**Do not jump weeks.** Finish the current week before touching the next. The user advances the cadence explicitly.

Within a week, **work in checkpointed blocks**. Pause between blocks (setup → SKILL.md refactor → state manager → phase files → token instrumentation → real test) and let the user review. Do not generate many files in a row without a pause.

## Strategic decisions (do not revisit without strong reason)

These are settled and documented in the plan. Do not re-litigate:

| Decision | Why it matters |
|---|---|
| Externalized state in `.sop-session/state.json` | Eliminates exponential context growth. The skill never relies on chat history surviving turns. |
| Lazy-loaded phases — `SKILL.md` is a thin router (~60 lines) | Phase instructions live in `core/phases/*.md`, loaded only when needed. ~50% reduction in fixed per-turn cost. |
| Filesystem required | Targets are Claude Code, Claude Cowork, OpenClaw. Plain Claude Desktop without filesystem MCP is not supported. |
| English internals, user-language dialogue | All skill instructions, manifest fields, file paths, IDs, code, comments, and markdown artifacts are in English. Conversation with the user follows the user's language. Generated SOP *content* is in the user's language. |
| Inferred deployment target with plain-language confirmation | The skill silently classifies each SOP (`HUMAN_TRIGGERED`, `TIME_OR_EVENT_TRIGGERED`, `AMBIGUOUS`) and confirms with the user in plain words ("conversational assistant", "automation"), not framework names. |
| CrewAI is flagship, OpenClaw is secondary | Adapter priority and example budget reflect this. |

## Repository structure (planned)

The tree below is the target layout. Most directories will be empty with `.gitkeep` until populated week by week.

```
sop-forge/
├── core/                  ← the skill itself
│   ├── SKILL.md           ← router + invariants (~60 lines)
│   ├── phases/            ← A-context, B-brainstorm, D-generate, E-review, F-closing
│   ├── references/        ← sectoral knowledge, templates
│   └── scripts/           ← state-manager.py, token-budget.py
├── spec/                  ← agent-manifest-v1.md + JSON schema
├── adapters/
│   ├── crewai/            ← flagship: produces Python multi-agent code
│   └── claude-subagent/   ← produces .claude/agents/*.md
├── integrations/
│   └── openclaw/          ← produces Molty-compatible skills
├── examples/              ← end-to-end real-world cases
├── benchmarks/            ← token consumption: before vs after
└── docs/                  ← plan, architecture, token-economy article, manifest spec
```

## Skill architecture invariants

When working on `core/`:

- `SKILL.md` is a router. Do not inline phase content. Every phase lives in `core/phases/<letter>-<name>.md` and is referenced by name only.
- Always read `.sop-session/state.json` at the start of any continuation. Never reconstruct state from chat history.
- After writing a generated SOP file to disk, **do not display its content back into chat**. Show a summary (step count, owner, key risks) and the path. This is a token-economy invariant, not a stylistic preference.
- Backlog status, business context, language, translations, and `current_pop_notes` all belong in `state.json`. The schema is owned by `core/scripts/state-manager.py`.
- `[A DEFINIR]` (or English equivalent: `[TBD]`) is the escape hatch when the user does not know an answer. Do not block on missing details.

## Working norms for this collaboration

- **Communicate with the user in Brazilian Portuguese.** All committed artifacts (code, markdown, manifests, paths, identifiers, comments) are in English. Do not ask the user to reconfirm this.
- **Be terse.** This project's whole purpose is token economy; verbose responses contradict its values. No long preambles, no celebratory recaps after each step.
- **Honesty over creativity.** If the plan is wrong, say so before coding. If you hit a technical obstacle mid-execution, stop and surface it — do not invent a workaround that will bite in week 3.
- **No heroics.** The plan assumes 8–12 focused hours per week. Cutting features beats compromising quality. By Wednesday of Week 4, no new feature work — README polish only.

## Source-of-truth files (local-only, gitignored under `.private/`)

- `.private/plan/sop-forge-4-week-plan.md` — strategic plan, deliverables, week-by-week checklist, risks.
- `.private/plan/skill.md` — the legacy `pop-generator` skill being refactored. Do not discard its content; translate, modularize, and improve.
- `.private/plan/prompt.md` — the bootstrap brief for the assistant, including the Block 1–4 checkpoint structure for the first session.

## Commands

There is no build, test, or lint tooling yet — Week 1 has not produced executable code as of this writing. As scripts and adapters land, document their commands here. The plan calls for:

- `core/scripts/state-manager.py` — read/write `.sop-session/state.json`
- `core/scripts/token-budget.py` — approximate session token usage
- `adapters/crewai/` — Python package (`pyproject.toml` or `setup.py`)
- `sop-forge install-openclaw [path-to-sops]` — CLI command (Week 3)

Do not invent commands or scaffolding ahead of the week that introduces them.
