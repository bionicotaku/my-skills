# Heartbeat Rules

Heartbeat exists to keep the promoted layer tidy and trustworthy.

## Scope

Heartbeat only operates on:

```text
~/self-improving/
```

It does not maintain raw capture in:

```text
~/.openclaw/workspace/.learnings/
```

It does not write runtime state into the installed skill directory.

## Start of Each Heartbeat

1. Ensure `~/self-improving/heartbeat-state.md` exists.
2. Write `last_heartbeat_started_at` in ISO 8601.
3. Read the previous `last_reviewed_change_at`.
4. Scan `~/self-improving/` for changes after that moment, excluding `heartbeat-state.md`.

## If Nothing Changed

- set `last_heartbeat_result: HEARTBEAT_OK`
- optionally append a short action note
- return `HEARTBEAT_OK`

## If Something Changed

Allowed actions:
- refresh `index.md` if counts or references drift
- lightly summarize or merge repetitive promoted notes when meaning is unchanged
- move clearly misplaced promoted notes to the right scope when the destination is unambiguous
- preserve explicit corrections and confirmed rules exactly
- update `last_reviewed_change_at` only after the review completes cleanly

## Strict Prohibitions

Heartbeat must not:
- promote lessons out of `.learnings/`
- infer durable preferences from silence
- create new long-term rules from weak evidence
- delete promoted history wholesale
- reorganize files outside `~/self-improving/`

When scope is unclear, leave the content where it is and record a suggested follow-up instead of guessing.
