# core/scripts

Helper scripts for sop-forge session management. Stdlib-only — no external dependencies.

## state-manager.py

Reads and writes the durable session state for a SOP generation run. The skill is required to
read this file at the start of every turn instead of relying on chat history.

State location: `./.sop-session/state.json` by default. Override with the `SOP_SESSION_DIR`
environment variable. The directory is created on first write. All writes are atomic
(temp file + `os.replace`).

### State schema (v1)

```json
{
  "schema_version": 1,
  "language": "pt-BR",
  "business": {
    "name": "Clínica X",
    "sector": "aesthetic clinic",
    "size": "5-20",
    "primary_motivation": "team scaling"
  },
  "translations": {},
  "backlog": [
    {
      "id": "POP-01",
      "area": "ATTENDANCE",
      "name": "client-checkin",
      "display_name": "Check-in do cliente",
      "status": "pending",
      "target_category": null
    }
  ],
  "current_pop_notes": {
    "pop_id": "POP-01",
    "trigger": "client arrives at front desk",
    "owner": "receptionist",
    "steps": ["greet", "verify appointment"],
    "risks": ["wrong patient identification"],
    "resources": ["scheduling app"],
    "target_category": "HUMAN_TRIGGERED"
  }
}
```

### Field semantics

- `schema_version` — bump on breaking schema changes; consumers should refuse unknown versions.
- `language` — IETF BCP 47 tag (`pt-BR`, `en-US`, ...) for the user's conversation language.
- `business` — fixed-key object capturing the result of Phase A. Use `null` for unknown fields.
- `translations` — free-form key-value map for sector or locale-specific terms used during generation.
- `backlog[]` — ordered list of POPs to generate.
  - `id` — `POP-NN`, auto-assigned by `add-pop`.
  - `area` — ALL-CAPS English label (e.g. `ATTENDANCE`, `PROCEDURES`).
  - `name` — English kebab-case identifier used in generated file paths.
  - `display_name` — optional user-language label for chat output.
  - `status` — `pending` | `in_progress` | `completed` | `skipped`.
  - `target_category` — see below; `null` until inference resolves it.
- `current_pop_notes` — structured notes for the in-flight POP, or `null` between POPs.

### Target categories

- `HUMAN_TRIGGERED` — a person initiates the action (walk-in, request, decision).
- `TIME_OR_EVENT_TRIGGERED` — a clock or external event initiates it (cron, webhook, threshold).
- `AMBIGUOUS` — signals are mixed; Phase B should ask one disambiguating question, then re-classify.

### CLI

| Command | Purpose |
|---|---|
| `init [--language LANG] [--force]` | Create `state.json` with defaults |
| `show` | Print current state |
| `set --json PATCH` | Deep-merge a JSON object into state (lists and scalars are replaced) |
| `add-pop --area A --name N [--display-name DN] [--target-category TC]` | Append to backlog |
| `update-pop ID [--status S] [--target-category TC] [--display-name DN]` | Update a backlog entry |
| `set-notes --json NOTES` | Set `current_pop_notes` |
| `clear-notes` | Set `current_pop_notes` to `null` |
| `path` | Print resolved state file path |

To unset a field that the focused subcommands do not cover, use `set --json` with an explicit
`null`.

### Examples

```bash
# Start a new session
python core/scripts/state-manager.py init --language pt-BR

# Capture business context (Phase A)
python core/scripts/state-manager.py set --json '{
  "business": {"name": "Clínica X", "sector": "aesthetic clinic", "size": "5-20"}
}'

# Add a POP and mark it in progress
python core/scripts/state-manager.py add-pop \
  --area ATTENDANCE --name client-checkin --display-name "Check-in do cliente"
python core/scripts/state-manager.py update-pop POP-01 --status in_progress

# Capture brainstorm notes (Phase B)
python core/scripts/state-manager.py set-notes --json '{
  "pop_id": "POP-01",
  "trigger": "client arrives at front desk",
  "owner": "receptionist",
  "steps": ["greet", "verify appointment"],
  "risks": ["wrong patient identification"],
  "resources": ["scheduling app"],
  "target_category": "HUMAN_TRIGGERED"
}'

# After generation, mark complete and clear notes
python core/scripts/state-manager.py update-pop POP-01 --status completed
python core/scripts/state-manager.py clear-notes
```

### Module API

The same primitives are available as importable functions. Because the filename has a hyphen,
use `importlib.util` rather than a normal `import`:

```python
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location(
    "state_manager", pathlib.Path("core/scripts/state-manager.py")
)
sm = importlib.util.module_from_spec(spec); spec.loader.exec_module(sm)

state = sm.load()
sm.add_pop(state, area="ATTENDANCE", name="client-checkin")
sm.save(state)
```

Public functions: `default_state`, `load`, `save`, `deep_merge`, `next_pop_id`, `add_pop`,
`update_pop`, `set_notes`, `clear_notes`, `state_path`, `state_dir`.
