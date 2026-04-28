#!/usr/bin/env python3
"""state-manager.py — durable session state for sop-forge.

State lives at $SOP_SESSION_DIR/state.json (default: ./.sop-session/state.json).
The skill must read this file at the start of every turn instead of relying on
chat history. See core/scripts/README.md for the schema.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

VALID_STATUSES = {"pending", "in_progress", "completed", "skipped"}
VALID_TARGETS = {"HUMAN_TRIGGERED", "TIME_OR_EVENT_TRIGGERED", "AMBIGUOUS"}
NOTES_FIELDS = {"pop_id", "trigger", "owner", "steps", "risks", "resources", "target_category"}
BUSINESS_FIELDS = ("name", "sector", "size", "primary_motivation")


def state_dir() -> Path:
    override = os.environ.get("SOP_SESSION_DIR")
    return Path(override) if override else Path.cwd() / ".sop-session"


def state_path() -> Path:
    return state_dir() / "state.json"


def default_state(language: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "language": language,
        "business": {field: None for field in BUSINESS_FIELDS},
        "translations": {},
        "backlog": [],
        "current_pop_notes": None,
    }


def load() -> dict[str, Any]:
    p = state_path()
    if not p.exists():
        raise FileNotFoundError(
            f"state file not found at {p}. Run `state-manager.py init` first."
        )
    return json.loads(p.read_text(encoding="utf-8"))


def save(state: dict[str, Any]) -> None:
    p = state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=p.parent, delete=False, suffix=".tmp"
    )
    try:
        json.dump(state, tmp, ensure_ascii=False, indent=2)
        tmp.write("\n")
        tmp.flush()
        os.fsync(tmp.fileno())
    finally:
        tmp.close()
    os.replace(tmp.name, p)


def deep_merge(base: dict, patch: dict) -> dict:
    for key, value in patch.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def next_pop_id(backlog: list[dict]) -> str:
    used = {entry["id"] for entry in backlog if entry.get("id")}
    n = 1
    while f"POP-{n:02d}" in used:
        n += 1
    return f"POP-{n:02d}"


def add_pop(
    state: dict,
    *,
    area: str,
    name: str,
    display_name: str | None = None,
    target_category: str | None = None,
) -> dict:
    if target_category is not None and target_category not in VALID_TARGETS:
        raise ValueError(f"invalid target_category: {target_category}")
    entry = {
        "id": next_pop_id(state["backlog"]),
        "area": area,
        "name": name,
        "display_name": display_name,
        "status": "pending",
        "target_category": target_category,
    }
    state["backlog"].append(entry)
    return entry


def update_pop(
    state: dict,
    pop_id: str,
    *,
    status: str | None = None,
    target_category: str | None = None,
    display_name: str | None = None,
) -> dict:
    for entry in state["backlog"]:
        if entry["id"] == pop_id:
            if status is not None:
                if status not in VALID_STATUSES:
                    raise ValueError(f"invalid status: {status}")
                entry["status"] = status
            if target_category is not None:
                if target_category not in VALID_TARGETS:
                    raise ValueError(f"invalid target_category: {target_category}")
                entry["target_category"] = target_category
            if display_name is not None:
                entry["display_name"] = display_name
            return entry
    raise KeyError(f"pop id {pop_id} not found in backlog")


def set_notes(state: dict, notes: dict) -> dict:
    extra = set(notes.keys()) - NOTES_FIELDS
    if extra:
        raise ValueError(f"unknown notes fields: {sorted(extra)}")
    tc = notes.get("target_category")
    if tc is not None and tc not in VALID_TARGETS:
        raise ValueError(f"invalid target_category: {tc}")
    state["current_pop_notes"] = notes
    return notes


def clear_notes(state: dict) -> None:
    state["current_pop_notes"] = None


def _emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def cmd_init(args) -> int:
    p = state_path()
    if p.exists() and not args.force:
        print(f"state already exists at {p}; use --force to overwrite", file=sys.stderr)
        return 1
    state = default_state(language=args.language)
    save(state)
    _emit(state)
    return 0


def cmd_show(args) -> int:
    _emit(load())
    return 0


def cmd_set(args) -> int:
    patch = json.loads(args.json)
    if not isinstance(patch, dict):
        print("--json must be a JSON object", file=sys.stderr)
        return 2
    state = load()
    deep_merge(state, patch)
    save(state)
    _emit(state)
    return 0


def cmd_add_pop(args) -> int:
    state = load()
    entry = add_pop(
        state,
        area=args.area,
        name=args.name,
        display_name=args.display_name,
        target_category=args.target_category,
    )
    save(state)
    _emit(entry)
    return 0


def cmd_update_pop(args) -> int:
    state = load()
    entry = update_pop(
        state,
        args.id,
        status=args.status,
        target_category=args.target_category,
        display_name=args.display_name,
    )
    save(state)
    _emit(entry)
    return 0


def cmd_set_notes(args) -> int:
    notes = json.loads(args.json)
    if not isinstance(notes, dict):
        print("--json must be a JSON object", file=sys.stderr)
        return 2
    state = load()
    set_notes(state, notes)
    save(state)
    _emit(notes)
    return 0


def cmd_clear_notes(args) -> int:
    state = load()
    clear_notes(state)
    save(state)
    print("ok")
    return 0


def cmd_path(args) -> int:
    print(state_path())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="sop-forge session state manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="initialize a new state file")
    p_init.add_argument("--language", default=None, help="IETF tag, e.g. pt-BR")
    p_init.add_argument("--force", action="store_true", help="overwrite if exists")
    p_init.set_defaults(func=cmd_init)

    p_show = sub.add_parser("show", help="print current state as JSON")
    p_show.set_defaults(func=cmd_show)

    p_set = sub.add_parser("set", help="deep-merge a JSON patch into state")
    p_set.add_argument("--json", required=True, help='e.g. {"language": "pt-BR"}')
    p_set.set_defaults(func=cmd_set)

    targets = sorted(VALID_TARGETS)
    p_add = sub.add_parser("add-pop", help="append a POP to the backlog")
    p_add.add_argument("--area", required=True)
    p_add.add_argument("--name", required=True, help="English kebab-case identifier")
    p_add.add_argument("--display-name", default=None)
    p_add.add_argument("--target-category", default=None, choices=targets)
    p_add.set_defaults(func=cmd_add_pop)

    p_upd = sub.add_parser("update-pop", help="update a backlog entry")
    p_upd.add_argument("id", help="POP id, e.g. POP-01")
    p_upd.add_argument("--status", default=None, choices=sorted(VALID_STATUSES))
    p_upd.add_argument("--target-category", default=None, choices=targets)
    p_upd.add_argument("--display-name", default=None)
    p_upd.set_defaults(func=cmd_update_pop)

    p_notes = sub.add_parser("set-notes", help="set current_pop_notes")
    p_notes.add_argument("--json", required=True, help="JSON object with notes fields")
    p_notes.set_defaults(func=cmd_set_notes)

    p_clear = sub.add_parser("clear-notes", help="clear current_pop_notes")
    p_clear.set_defaults(func=cmd_clear_notes)

    p_path = sub.add_parser("path", help="print resolved state file path")
    p_path.set_defaults(func=cmd_path)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
