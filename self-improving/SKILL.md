---
name: Self-Improving
description: "Canonical OpenClaw self-improvement workflow. Capture raw incidents in workspace .learnings/, promote only durable rules into ~/self-improving/, maintain promoted memory conservatively, and keep the behavior auditable."
metadata:
  {
    "clawdbot":
      {
        "emoji": "🧠",
        "requires": { "bins": [] },
        "os": ["linux", "darwin", "win32"],
        "configPaths": ["~/self-improving/"],
        "configPaths.optional":
          [
            "~/.openclaw/workspace/.learnings/",
            "./AGENTS.md",
            "./SOUL.md",
            "./HEARTBEAT.md",
          ],
      },
  }
---

## Purpose

This is the canonical self-improvement skill for OpenClaw.

Use it when:

- a command, tool, API, or workflow fails
- the user corrects you
- you discover a knowledge gap
- you identify a reusable lesson
- you need to decide whether a lesson stays raw or becomes long-term guidance

The skill implements one model only:

- raw incident capture lives in workspace `.learnings/`
- promoted long-term guidance lives in `~/self-improving/`

## Dual-Layer Model

### Raw Layer

OpenClaw workspace path:

```text
~/.openclaw/workspace/.learnings/
├── ERRORS.md
├── LEARNINGS.md
└── FEATURE_REQUESTS.md
```

Purpose:

- record failures, first corrections, tentative lessons, knowledge gaps, and missing capabilities
- preserve the original event before any promotion
- keep ambiguous or one-off signals out of long-term memory

### Promoted Layer

User-level path:

```text
~/self-improving/
├── memory.md
├── corrections.md
├── index.md
├── heartbeat-state.md
├── domains/
└── projects/
```

Purpose:

- store durable preferences and rules
- track corrections with lasting value
- keep domain and project guidance scoped correctly
- support conservative heartbeat maintenance

`~/self-improving/` is not a raw capture layer.
`.learnings/` is not long-term memory.

## Routing Table

| Situation                                         | Write To                                               | Why                          |
| ------------------------------------------------- | ------------------------------------------------------ | ---------------------------- |
| Command, tool, API, or workflow failure           | `~/.openclaw/workspace/.learnings/ERRORS.md`           | Raw incident log             |
| Missing capability or unmet request               | `~/.openclaw/workspace/.learnings/FEATURE_REQUESTS.md` | Capability gap               |
| First correction, tentative lesson, knowledge gap | `~/.openclaw/workspace/.learnings/LEARNINGS.md`        | Tentative until confirmed    |
| Explicit durable correction with lasting value    | `~/self-improving/corrections.md`                      | Long-term correction history |
| Durable global preference or reusable rule        | `~/self-improving/memory.md`                           | Global promoted guidance     |
| Domain-level recurring pattern                    | `~/self-improving/domains/<domain>.md`                 | Scoped long-term pattern     |
| Project-specific long-term override               | `~/self-improving/projects/<project>.md`               | Project-only override        |

Default behavior:

- first occurrence stays in `.learnings/`
- ambiguous scope stays in `.learnings/`
- promotion happens later, not during initial capture

## Promotion Rules

Promote from `.learnings/` to `~/self-improving/` only when at least one of these is true:

1. the user explicitly says the rule should stick
2. the same lesson appears 3 times
3. the pattern succeeds across multiple tasks and is clearly reusable
4. the scope is clearly a durable domain or project rule

Promotion rules:

- promote to the smallest correct scope
- keep the source path auditable from raw capture to promoted rule
- prefer explicit evidence over inference
- keep promoted memory sparse and high-signal

Never do these:

- do not promote on first occurrence unless the human clearly confirms it
- do not infer long-term preferences from silence
- do not treat a one-off file instruction as a general rule
- do not let heartbeat invent promotions from weak evidence

## Heartbeat Rules

Heartbeat only maintains the promoted layer in `~/self-improving/`.

Allowed heartbeat actions:

- refresh `index.md` if counts or references drift
- lightly compact repetitive promoted notes without changing meaning
- move clearly misplaced promoted notes when the target scope is unambiguous
- update `heartbeat-state.md`

Not allowed:

- no automatic promotion from `.learnings/`
- no guessing new rules from repeated silence
- no broad rewrites of promoted memory
- no writes to skill installation directories as runtime state

Read `heartbeat-rules.md` for the stable contract.

## Security Boundaries

Security rules apply to both layers:

- raw capture in `.learnings/`
- promoted memory in `~/self-improving/`

Never store:

- credentials, tokens, keys
- financial, medical, or biometric data
- third-party personal information
- sensitive access patterns or private location routines

Read `boundaries.md` before expanding what gets stored.

## OpenClaw Setup / Recovery

This skill assumes OpenClaw is the primary environment.

Minimal runtime paths:

- `~/.openclaw/workspace/.learnings/`
- `~/self-improving/`

Minimal workspace guidance:

- `AGENTS.md` should route raw incidents into `.learnings/` and promoted rules into `~/self-improving/`
- `SOUL.md` should reinforce retrieval before non-trivial work and conservative promotion
- `HEARTBEAT.md` should point at `heartbeat-rules.md` and `~/self-improving/heartbeat-state.md`

Optional recovery hook:

```bash
cp -r hooks/openclaw ~/.openclaw/hooks/self-improvement
openclaw hooks enable self-improvement
```

Read `setup.md` for the non-destructive setup and recovery flow.

## References

Keep the reference set small:

- `setup.md`
- `heartbeat-rules.md`
- `boundaries.md`
- `references/examples.md`

## Non-Goals

This skill does not:

- store runtime state in the installed skill directory
- create an alternate memory system inside the repo
- ship repo-level Claude/Codex hook scaffolding
- extract new skills as part of the default workflow
- run heavy automatic promotion, demotion, or archive passes
- infer durable preferences from silence or single events
- provide export, forget, wipe, or other management workflows by default

If a behavior is not part of the two-layer OpenClaw model above, do not add it back casually.
