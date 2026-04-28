#!/usr/bin/env python3
"""token-budget.py — approximate token consumption of a session transcript.

Method: character-based heuristic. tokens ≈ characters / chars_per_token.
Default chars_per_token = 3.5 (rough fit for mixed Portuguese / English content).

Anthropic does not publish an official offline tokenizer. For exact counts, use the
Anthropic API's token-count endpoint. This script prioritizes reproducibility — stdlib only,
deterministic, no network — over precision. See benchmarks/method.md for accuracy limits.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_CHARS_PER_TOKEN = 3.5

SPEAKER_RE = re.compile(
    r"^\s*>?\s*(Human|User|Assistant|Claude|AI)\s*:\s*",
    re.IGNORECASE,
)


def estimate_tokens(text: str, chars_per_token: float = DEFAULT_CHARS_PER_TOKEN) -> int:
    return round(len(text) / chars_per_token)


def split_by_speaker(text: str) -> dict[str, str]:
    """Split a transcript by speaker tags. Returns {speaker: concatenated_text}.

    If no speaker tags are detected, returns {"total": text}.
    """
    parts: dict[str, list[str]] = {}
    current: str | None = None
    buf: list[str] = []

    def flush() -> None:
        nonlocal buf
        if current is not None and buf:
            parts.setdefault(current, []).append("".join(buf))
            buf = []

    for line in text.splitlines(keepends=True):
        m = SPEAKER_RE.match(line)
        if m:
            flush()
            current = m.group(1).lower()
        elif current is None:
            current = "preamble"
        buf.append(line)
    flush()

    has_real_speaker = any(k for k in parts if k != "preamble")
    if not has_real_speaker:
        return {"total": text}

    return {k: "".join(v) for k, v in parts.items()}


def analyze(text: str, chars_per_token: float, by_speaker: bool) -> dict[str, Any]:
    if by_speaker:
        per = {
            k: {"chars": len(v), "tokens": estimate_tokens(v, chars_per_token)}
            for k, v in split_by_speaker(text).items()
        }
        return {
            "chars": sum(p["chars"] for p in per.values()),
            "tokens": sum(p["tokens"] for p in per.values()),
            "by_speaker": per,
        }
    return {"chars": len(text), "tokens": estimate_tokens(text, chars_per_token)}


def render_human(result: dict[str, Any]) -> str:
    out: list[str] = [f"Method: chars / {result['chars_per_token']}"]
    if "files" in result:
        for path, d in result["files"].items():
            out.append(f"\n{path}")
            out.append(f"  chars:  {d['chars']}")
            out.append(f"  tokens: ~{d['tokens']}")
            if "by_speaker" in d:
                for sp, sd in d["by_speaker"].items():
                    out.append(
                        f"    {sp:12s} chars={sd['chars']:>8d} tokens=~{sd['tokens']:>6d}"
                    )
        out.append(f"\nTotal chars:  {result['total']['chars']}")
        out.append(f"Total tokens: ~{result['total']['tokens']}")
    else:
        d = result["stdin"]
        out.append(f"chars:  {d['chars']}")
        out.append(f"tokens: ~{d['tokens']}")
        if "by_speaker" in d:
            for sp, sd in d["by_speaker"].items():
                out.append(f"  {sp:12s} chars={sd['chars']:>8d} tokens=~{sd['tokens']:>6d}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Approximate token consumption from a transcript."
    )
    parser.add_argument("files", nargs="*", help="Transcript files; stdin if omitted.")
    parser.add_argument(
        "--chars-per-token",
        type=float,
        default=DEFAULT_CHARS_PER_TOKEN,
        help=f"Characters per token (default {DEFAULT_CHARS_PER_TOKEN}).",
    )
    parser.add_argument(
        "--by-speaker",
        action="store_true",
        help="Break down counts by Human/Assistant when speaker tags are present.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args(argv)

    if args.chars_per_token <= 0:
        print("chars-per-token must be positive", file=sys.stderr)
        return 2

    if args.files:
        per_file = {
            f: analyze(Path(f).read_text(encoding="utf-8"), args.chars_per_token, args.by_speaker)
            for f in args.files
        }
        result: dict[str, Any] = {
            "method": "chars_per_token",
            "chars_per_token": args.chars_per_token,
            "files": per_file,
            "total": {
                "chars": sum(d["chars"] for d in per_file.values()),
                "tokens": sum(d["tokens"] for d in per_file.values()),
            },
        }
    else:
        result = {
            "method": "chars_per_token",
            "chars_per_token": args.chars_per_token,
            "stdin": analyze(sys.stdin.read(), args.chars_per_token, args.by_speaker),
        }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(render_human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
