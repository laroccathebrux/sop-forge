# Token measurement methodology

How sop-forge approximates token consumption for the token-economy benchmark.

## Tool

`core/scripts/token-budget.py` — character-based heuristic, stdlib only, deterministic, no
network calls.

```bash
python core/scripts/token-budget.py [--chars-per-token N] [--by-speaker] [--json] FILE...
```

## Method

```
tokens ≈ characters / chars_per_token
```

Default `chars_per_token = 3.5`, picked as a rough fit for mixed Portuguese / English
content. Override per language with `--chars-per-token N`. Suggested starting points:

| Language mix | `chars_per_token` |
|---|---|
| English-only prose | 4.0 |
| Mixed PT / EN (default) | 3.5 |
| Portuguese-only prose | 3.0 |
| Code-heavy | 3.0 |

These values are starting points, not measurements. Calibrate against a known sample if you
need higher confidence.

## Why a character heuristic

- Anthropic does not publish an official offline tokenizer.
- The Anthropic API has a token-count endpoint, but using it requires network access and an
  API key. That undermines reproducibility — the benchmark should be runnable offline by
  any third party with the same transcript.
- `tiktoken` (OpenAI) gives a tokenizer-shaped approximation but introduces an external
  dependency and is not Anthropic-faithful.
- Character heuristic is deterministic, dependency-free, and platform-agnostic. Good enough
  for *directional* benchmarks where the headline number is a relative before/after delta,
  not an exact absolute count.

## Accuracy limits

- **Magnitude error: ±20%** in typical mixed prose; can rise to ±30% for code-heavy or
  table-heavy transcripts. Always frame absolute numbers as "approximately N tokens", never
  as exact counts.
- **Not Anthropic-faithful.** Real Claude tokenization differs from any offline heuristic.
- **Whitespace, markdown syntax, and prose are weighted equally** by the heuristic, but
  Claude's tokenizer compresses common patterns more aggressively. Markdown-heavy files
  will be slightly over-counted; long URLs and rare strings under-counted.
- **Speaker prefixes are counted as part of the content** when present. If the transcript
  format adds metadata (timestamps, message IDs, system reminders), strip those before
  running for a cleaner comparison.

## Benchmark procedure

To produce a comparable before/after measurement:

1. Run the same business case end-to-end on both `pop-generator` (legacy) and `sop-forge`,
   producing the same number of SOPs from the same brainstorm content.
2. Save each session transcript verbatim to a `.txt` file. Use stable speaker prefixes —
   `Human:` / `Assistant:` are detected by `--by-speaker`.
3. Append the loaded skill files (router + any phase files actually loaded) to the
   transcript so the count includes the skill's contribution to the prompt budget.
4. Run `token-budget.py` on each transcript with the same `--chars-per-token` value.
5. Record both totals plus the per-speaker breakdown in `benchmarks/results-*.md`.

The benchmark report should:

- Quote the methodology version (commit hash of this file at the time of measurement).
- Report both `chars` and `tokens` for transparency.
- Note any deviations from the standard procedure.
- Frame the headline as a **relative** improvement, e.g. "≈40% reduction in input tokens
  per SOP", not "exactly N tokens saved".

## Sanity check

The heuristic is deterministic — running the script twice on the same input must produce
identical numbers. If they differ, the input file changed between runs.

```bash
python core/scripts/token-budget.py session.txt
python core/scripts/token-budget.py session.txt
# Identical output expected.
```
