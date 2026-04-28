# Phase F — Closing

Loaded when the user wants to wrap up the session, either because the backlog is empty or
because they explicitly stopped early.

## Step 1 — Write `INDEX.md`

Generate `sops/INDEX.md` with relative links to every SOP whose backlog entry has
`status == "completed"`, grouped by `area`. The index body is in the user's language.
Skipped and pending entries are not listed.

Skeleton (translate area headings to user's language):

```markdown
# SOP index — <business name>

## Front-of-house
- [POP-01 — Client check-in](FRONT_OF_HOUSE/POP-01-front-of-house-client-checkin.md)

## Service delivery
- [POP-03 — Skin cleansing](SERVICE_DELIVERY/POP-03-service-delivery-skin-cleansing.md)
```

If there are zero completed entries, skip writing `INDEX.md` and tell the user nothing was
generated this session.

## Step 2 — Final summary

Translate the example below to the user's language. Pull paths and counts from `state.json`,
not from chat history.

> "🎉 Session done.
>
> ```
> sops/
> ├── INDEX.md
> ├── FRONT_OF_HOUSE/
> │   └── POP-01-front-of-house-client-checkin.md
> └── SERVICE_DELIVERY/
>     └── POP-03-service-delivery-skin-cleansing.md
> ```
>
> Generated: 2 POPs. Pending in backlog: 3 (we can resume next session)."

Pending count = entries with `status == "pending"`. Skipped count is reported only if it is
greater than zero.

## Step 3 — Continuity note

Tell the user the session is resumable. Translate:

> "Your session is saved at `.sop-session/state.json`. Reopen this directory next time and
> the skill will pick up the pending POPs from where we left off."

Do **not** delete or modify `state.json` here. The next session will read it and skip
Phase A automatically because `business` is already populated.

## Exit

Phase F is the terminal phase. After it runs, the skill is idle until the user starts a new
turn.
