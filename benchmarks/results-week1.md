# Week 1 — sop-forge token budget (initial measurement)

| Field | Value |
|---|---|
| Date | 2026-04-29 |
| Skill commit at test time | `1c9fce4` |
| Method document | `benchmarks/method.md` |
| Method | `tokens ≈ chars / 3.5` (mixed PT/EN heuristic) |
| Magnitude error | ±20% (per `method.md`) |
| Host | Claude Code v2.1.123, Opus 4.7, project-level skill install |

---

## Test case

End-to-end session in Claude Code with `sop-forge` installed at
`~/Documents/sop-forge-test/.claude/skills/sop-forge` (symlink to `core/`).

Business: **Sofiq** — small tech-services company (2–5 people). The user opened with a
directed intent: build an OpenClaw "manager" agent that audits CRM processes (Kommo) and
emails alerts when leads are not followed up within 4 business days.

The user came in with a single specific use case rather than a generic "I want to document
my processes". The skill responded by skipping Phase B Mode 1 (broad backlog construction
from sectoral hints) and proceeding directly to per-SOP brainstorm for the one POP the user
described. See **UX observations / issue #2** below.

## Token counts

| Bucket | Chars | ~Tokens |
|---|---:|---:|
| Preamble (Claude Code UI header box) | 892 | 255 |
| Human (user inputs) | 1,423 | 407 |
| Assistant (skill output incl. tool calls) | 6,723 | 1,921 |
| **Total** | **9,038** | **~2,583** |

Pure session content, excluding the local UI preamble: **8,146 chars / ~2,328 tokens**.

Reported numbers are directional, not exact. The character heuristic is dependency-free and
deterministic but not Anthropic-faithful — see `method.md` for accuracy limits.

## Output

One SOP generated end-to-end:

- `sops/MANAGEMENT/POP-01-management-crm-process-audit.md` — 69 lines, full template fill,
  `target_category: TIME_OR_EVENT_TRIGGERED`. All sections populated; no `[TBD]` (the user
  provided full detail in two depth rounds).

`sops/INDEX.md` was not written — Phase F never executed because the user ended the session
before triggering the close. See **issue #4** below.

## Phase coverage

| Phase | Reached? | Notes |
|---|---|---|
| A — Business context | ✓ | Single round, 3 questions in one block |
| B Mode 1 — Backlog construction | _Skipped (adaptive)_ | Skill detected the user had one specific POP in mind and offered to skip the broad backlog. See issue #2. |
| B Mode 2 — Per-SOP brainstorm | ✓ | Two depth rounds; classification `TIME_OR_EVENT_TRIGGERED` |
| D — Generate SOP | ✓ | Plain-language target announcement; no framework name surfaced |
| E — Review | ✓ | Summary-only output (no file body echoed); user approved with "aprovado." |
| F — Closing | ✗ | Not reached |

## Comparison vs `pop-generator` legacy

**No measured A/B comparison this week.** The legacy `pop-generator` was not re-run on a
matched scenario.

Qualitative baseline only: the legacy skill triggered a real rate-limit incident in
production use ("esgotou meu rate limit em poucos minutos após acumular contexto" — the
originating problem statement for this project). A measured A/B benchmark on the same
business case is recommended for Week 2 or 3 once the manifest spec has stabilized.

The 2,583-token figure for one full SOP end-to-end is consistent with the design intent of
the refactor (lazy-loaded phases, externalized state, no chat-history-dependent context),
but should not be reported as an "Nx reduction" without a paired measurement.

## UX observations

### Worked

- **Adaptive skip of Phase B Mode 1.** When the user came in with a directed intent, the
  skill offered to skip the broad backlog construction and focus on the one POP. Felt
  natural; saved tokens.
- **Plain-language target confirmation.** "Estou tratando isso como uma automação que roda
  em horário programado". No mention of CrewAI / OpenClaw / Claude sub-agent at this step.
- **Summary-only review.** Phase E produced a tight 4-bullet summary (step count, owner,
  watch-fors). The 69-line SOP body was not pasted into chat.
- **Agent-realizable output.** User feedback: *"voltado a um agente autônomo, sem passos não
  realizaveis agenticamente"*. The Phase D prompt is producing the right kind of content
  for downstream automation frameworks.

### Issues found

1. **`target_category` not propagated to backlog entry.** After Phase D confirmation, the
   classification appeared correctly in `current_pop_notes` and in the SOP frontmatter, but
   the backlog entry in `state.json` still showed `target_category: null`.
   *Fixed in D-generate.md as part of this checkpoint — `update-pop --target-category` is
   now called after agreement.*

2. **Adaptive Mode-1 skip is undocumented.** The behavior is good but `phases/B-brainstorm.md`
   does not describe it. A directed-intent user could just as easily get the full Mode 1
   treatment from a different LLM run, producing inconsistent UX.

3. **Phase D Step 1 reads as statement, not question.** Spec says "ask for confirmation".
   In practice the skill stated the classification and moved on without waiting for explicit
   agreement. Worked here because the inference was correct, but the user has no clean
   gate to course-correct mid-flow.

4. **Phase F never triggered automatically when backlog drained.** The skill asked an open
   question ("quer que eu encerre ou adicionar mais algum?") instead of running F when
   `pending == 0`. By spec, an empty backlog should drop into F. The current question gates
   that on user input.

### Backlog for Week 2

- [ ] **Phase D**: tighten Step 1 to actually wait for user agreement before generating
      (issue #3).
- [ ] **Phase E**: when transitioning and `pending == 0`, drop directly into F (issue #4).
- [ ] **Phase B Mode 1**: document the directed-intent skip path; make it deterministic
      rather than emergent (issue #2).
- [ ] Run a paired benchmark against `pop-generator` legacy on the same scenario to measure
      the headline token-economy delta (no measurement this week).

## Reproducibility

- Skill commit at test time: `1c9fce4`.
- Method commit: `5fa7622` (`benchmarks/method.md`).
- Transcript: not committed (private; lives in `~/Documents/sop-forge-test/`).
- Analysis tool: `core/scripts/token-budget.py --by-speaker --json <transcript>` against
  the saved Claude Code transcript.

## Appendix — final state.json

```json
{
  "schema_version": 1,
  "language": "pt-BR",
  "business": {
    "name": "Sofiq",
    "sector": "tech_services",
    "size": "2-5",
    "primary_motivation": "Automate internal processes using OpenClaw"
  },
  "translations": {},
  "backlog": [
    {
      "id": "POP-01",
      "area": "MANAGEMENT",
      "name": "crm-process-audit",
      "display_name": "Auditoria de processos no CRM",
      "status": "completed",
      "target_category": null
    }
  ],
  "current_pop_notes": null
}
```

The `target_category: null` here is the issue #1 above; the D-generate.md fix in this same
commit prevents it on future runs.
