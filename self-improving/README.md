# Self-Improving

Canonical OpenClaw self-improvement workflow.

This skill defines one explicit model:
- raw incidents are captured in workspace `.learnings/`
- durable rules are promoted into `~/self-improving/`

It is designed for OpenClaw first. The goal is not to build a second memory system inside the skill folder. The goal is to make learning from mistakes, corrections, and recurring patterns explicit, conservative, and auditable.

## When to Use

Use this skill when:
- the user corrects you or points out a mistake
- a command, tool, API, or workflow fails
- you realize your understanding was outdated or incomplete
- you discover a better approach worth retaining
- you complete significant work and want to evaluate what should remain raw versus what deserves promotion

Typical signals:
- "No, that's not right"
- "Actually, it should be..."
- "I prefer X, not Y"
- repeated failures with the same root cause
- the same workflow lesson showing up across multiple tasks

Do not use this skill to turn every one-off instruction into long-term memory. The canonical workflow is intentionally conservative.

## Architecture

The canonical model has two runtime layers.

### 1. Raw Capture Layer

Workspace path:

```text
~/.openclaw/workspace/.learnings/
├── ERRORS.md
├── LEARNINGS.md
└── FEATURE_REQUESTS.md
```

Purpose:
- record first-pass incidents
- preserve failures and tentative lessons before interpretation hardens into rules
- keep ambiguous scope and first occurrences out of long-term memory

What belongs here:
- command or tool failures
- first corrections
- knowledge gaps
- tentative lessons
- missing capabilities

### 2. Promoted Memory Layer

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
- store durable preferences and long-term rules
- keep correction history with lasting value
- scope reusable guidance to the correct level
- support conservative heartbeat maintenance

What belongs here:
- confirmed global preferences
- lasting corrections
- durable domain patterns
- project-specific long-term overrides

What does not belong here:
- raw error logs
- first-time lessons with unclear scope
- speculative patterns inferred from silence

### Installed Skill Layout

The installed skill itself stays small:

```text
self-improving/
├── SKILL.md
├── README.md
├── setup.md
├── heartbeat-rules.md
├── boundaries.md
├── hooks/
│   └── openclaw/
│       ├── HOOK.md
│       ├── handler.js
│       └── handler.ts
└── references/
    └── examples.md
```

The installed skill folder is documentation and bootstrap material. It is not runtime state.

## Quick Reference

| Topic | File |
|------|------|
| Canonical skill contract | `SKILL.md` |
| Detailed setup / recovery | `setup.md` |
| Heartbeat behavior | `heartbeat-rules.md` |
| Security boundaries | `boundaries.md` |
| Concrete examples | `references/examples.md` |
| Optional OpenClaw hook | `hooks/openclaw/HOOK.md` |

## Requirements

- no credentials required
- no extra binaries required
- OpenClaw is the primary intended environment
- optional hook setup uses OpenClaw's native hook system

## Core Model

The governing rule is simple:

1. capture first
2. promote later
3. promote narrowly
4. never infer durable rules from weak evidence

More concretely:
- first occurrence stays in `.learnings/`
- ambiguous scope stays in `.learnings/`
- confirmed durable guidance moves into `~/self-improving/`
- heartbeat only maintains promoted memory

## Routing Table

| Situation | Write To | Why |
|----------|----------|-----|
| Command, tool, API, or workflow failure | `~/.openclaw/workspace/.learnings/ERRORS.md` | Raw incident log |
| Missing capability or unmet request | `~/.openclaw/workspace/.learnings/FEATURE_REQUESTS.md` | Capability gap |
| First correction, tentative lesson, knowledge gap | `~/.openclaw/workspace/.learnings/LEARNINGS.md` | Tentative until confirmed |
| Explicit durable correction with lasting value | `~/self-improving/corrections.md` | Long-term correction history |
| Durable global preference or reusable rule | `~/self-improving/memory.md` | Global promoted guidance |
| Domain-level recurring pattern | `~/self-improving/domains/<domain>.md` | Scoped long-term rule |
| Project-specific long-term override | `~/self-improving/projects/<project>.md` | Project-only override |

Default behavior:
- raw first, promoted second
- smallest correct scope wins
- if in doubt, do not promote yet

## Learning Signals

These are strong signals to capture something.

### Corrections

Usually start in `.learnings/LEARNINGS.md`, unless the user makes the lasting nature explicit.

Examples:
- "No, that's not right..."
- "Actually, it should be..."
- "You're wrong about..."
- "That's outdated..."
- "I prefer X, not Y"
- "Remember that I always..."
- "Stop doing X"

### Preference Signals

Promote only if the user clearly expresses a durable preference.

Examples:
- "I like when you..."
- "Always do X for me"
- "Never do Y"
- "My style is..."
- "For this project, use..."

### Pattern Candidates

Keep these raw until there is enough evidence:
- same lesson appears 3 times
- same mitigation works repeatedly
- same workflow succeeds across multiple tasks

### Ignore by Default

Do not promote or over-learn from:
- one-time directives such as "do X now"
- file-local instructions such as "in this file..."
- hypotheticals such as "what if..."
- silence

## Self-Reflection

After significant work, pause and evaluate:

1. Did the outcome match the intent?
2. What could have been better?
3. Is there a reusable lesson here?
4. Is the lesson still tentative, or has it earned promotion?

When to self-reflect:
- after a multi-step task
- after bug fixing
- after receiving feedback
- when you notice your own output could be better

Recommended quick format:

```text
CONTEXT: [task type]
REFLECTION: [what went well or poorly]
LESSON: [what to do differently next time]
STATUS: tentative | promoted
```

Example:

```text
CONTEXT: Building Flutter UI
REFLECTION: Spacing looked off and required rework
LESSON: Check visual balance before presenting the screen
STATUS: tentative
```

If the same lesson proves useful repeatedly, it can be promoted using the same promotion rules as any other raw learning.

## Promotion Rules

Promote from `.learnings/` to `~/self-improving/` only when at least one of these is true:

1. the user explicitly says the rule should stick
2. the same lesson appears 3 times
3. the pattern works across multiple tasks and is clearly reusable
4. the scope is clearly a durable domain or project rule

Promotion rules:
- promote to the smallest correct scope
- keep the path from raw incident to promoted rule understandable
- prefer explicit evidence over guesswork
- keep promoted memory sparse and high-signal

Never do these:
- do not promote on first occurrence unless the human clearly confirms it
- do not infer durable preferences from silence
- do not treat a one-off file instruction as a standing rule
- do not let heartbeat invent promotions

## Namespace Rules

The promoted layer has explicit scopes.

### Global

File:
- `~/self-improving/memory.md`

Use for:
- durable preferences
- reusable global execution rules

### Correction History

File:
- `~/self-improving/corrections.md`

Use for:
- explicit corrections that retain long-term value
- durable "I got X wrong, correct answer is Y" history

### Domain Scope

Directory:
- `~/self-improving/domains/`

Use for:
- repeated patterns tied to a domain such as writing, coding, agent workflow, or communication

### Project Scope

Directory:
- `~/self-improving/projects/`

Use for:
- long-term overrides that only apply to a specific project

Conflict resolution:
1. project beats domain
2. domain beats global
3. if same scope conflicts, most recent confirmed rule wins
4. if still ambiguous, ask instead of guessing

## Logging Format

The canonical model does not require a rigid schema everywhere, but structured entries help with review and promotion.

### `ERRORS.md`

Recommended shape:

```markdown
## [ERR-YYYYMMDD-XXX] short_name

### Summary
Brief description of what failed

### Context
- command or operation
- relevant input
- reproducible: yes | no | unknown

### Suggested Follow-Up
Possible fix or next check
```

### `LEARNINGS.md`

Recommended shape:

```markdown
## [LRN-YYYYMMDD-XXX] category

### Summary
One-line lesson

### Context
What happened and why it mattered

### Status
tentative
```

Suggested categories:
- `correction`
- `knowledge_gap`
- `best_practice`

### `FEATURE_REQUESTS.md`

Recommended shape:

```markdown
## [FEAT-YYYYMMDD-XXX] capability_name

### Requested Capability
What was requested

### User Context
Why it matters

### Complexity
simple | medium | complex
```

### Promoted Entries

Promoted memory should be shorter and less incident-shaped.

Examples:

```markdown
## Response style
- Keep routine implementation close-outs concise unless the human asks for depth.
```

```markdown
## API workflow
- After OpenAPI changes, regenerate the client before type-checking.
```

For more examples, see [references/examples.md](/Users/evan/Documents/my-skills/self-improving/references/examples.md).

## Review and Promotion Workflow

Use this at natural checkpoints:
- before major work
- after major work
- when working in an area that has caused repeated issues

Suggested review loop:
1. scan recent `.learnings/`
2. identify duplicates or repeated lessons
3. check whether promotion criteria are met
4. promote only the durable rule, not the whole incident write-up
5. leave the raw source intact so the promotion path stays auditable

Useful checks:

```bash
rg -n "^## \\[" ~/.openclaw/workspace/.learnings
rg -n "Status|tentative|promoted" ~/.openclaw/workspace/.learnings
find ~/self-improving/domains ~/self-improving/projects -maxdepth 1 -type f -name "*.md" 2>/dev/null | sort
```

## Memory Retrieval

Before non-trivial work:

1. read `~/self-improving/memory.md`
2. list available domain and project files
3. read only the smallest matching files
4. do not read unrelated namespaces "just in case"

This keeps retrieval useful without bloating context.

## Quick Queries

If the user asks one of these, this is the intended behavior:

| User asks | Intended action |
|----------|-----------------|
| "What do you know about X?" | Search the relevant layer or scope for X |
| "What have you learned?" | Show recent high-signal entries from `.learnings/` or promoted memory |
| "Show my patterns" | Load `~/self-improving/memory.md` |
| "Show [project] patterns" | Load `~/self-improving/projects/<project>.md` |
| "What's in warm storage?" | List files under `domains/` and `projects/` |
| "Memory stats" | Report promoted-layer counts and recent raw activity |

Not part of the default canonical workflow:
- delete / forget flows
- export / zip flows
- automatic demotion or archive policy

## Memory Stats

A canonical "memory stats" response can look like:

```text
Self-Improving Memory

Raw layer:
  ERRORS.md: X entries
  LEARNINGS.md: X entries
  FEATURE_REQUESTS.md: X entries

Promoted layer:
  memory.md: X entries
  corrections.md: X entries
  domains/: X files
  projects/: X files

Recent activity (7 days):
  raw incidents logged: X
  promotions: X
```

This README does not define archive counts because archive/demotion is not part of the current canonical workflow.

## Common Traps

| Trap | Why It Fails | Better Move |
|------|--------------|-------------|
| Learning from silence | Creates fake preferences | Wait for explicit confirmation or repetition |
| Promoting too fast | Pollutes long-term memory | Keep first occurrences raw |
| Reading every namespace | Wastes context | Read HOT memory plus the smallest matching files |
| Treating incidents as rules | Loses nuance | Promote only the durable rule, keep incidents raw |
| Letting heartbeat guess | Creates hidden behavior drift | Keep heartbeat limited to promoted-layer maintenance |

## Heartbeat

Heartbeat only maintains `~/self-improving/`.

Allowed actions:
- refresh `index.md`
- lightly compact repetitive promoted notes without changing meaning
- move clearly misplaced promoted notes if the destination is obvious
- update `heartbeat-state.md`

Forbidden actions:
- promoting out of `.learnings/`
- inventing rules from weak evidence
- writing runtime state into the skill folder
- broad rewrites of promoted memory

See [heartbeat-rules.md](/Users/evan/Documents/my-skills/self-improving/heartbeat-rules.md).

## Security Boundaries

These rules apply to both raw and promoted layers.

Never store:
- passwords, tokens, API keys, SSH keys
- financial or medical data
- biometric data
- private third-party information
- sensitive access patterns

Store with caution:
- work context
- emotional state
- relationship context
- schedules

See [boundaries.md](/Users/evan/Documents/my-skills/self-improving/boundaries.md) for the full boundary model.

## OpenClaw Setup

OpenClaw is the primary target environment.

Expected runtime paths:

```text
~/.openclaw/workspace/.learnings/
~/self-improving/
```

Expected workspace steering:
- `AGENTS.md` routes raw incidents to `.learnings/` and durable rules to `~/self-improving/`
- `SOUL.md` reinforces retrieval before non-trivial work and conservative promotion
- `HEARTBEAT.md` points to this skill's heartbeat contract

Optional hook recovery:

```bash
cp -r hooks/openclaw ~/.openclaw/hooks/self-improvement
openclaw hooks enable self-improvement
```

That hook is intentionally minimal. It only injects a reminder for the two-layer workflow.

See [setup.md](/Users/evan/Documents/my-skills/self-improving/setup.md) for the detailed setup and recovery flow.

## Hook Integration

This skill supports one hook story only:
- OpenClaw native hook integration through `hooks/openclaw/`

It does not ship:
- Claude Code repo-level hook setup
- Codex repo-level hook setup
- shell scripts for activator / error detection

That is deliberate. The canonical skill is optimized for current OpenClaw behavior, not for cross-agent hook proliferation.

## Scope

This skill does:
- capture raw incidents in `.learnings/`
- promote durable rules into `~/self-improving/`
- maintain promoted memory conservatively through heartbeat
- document boundaries and setup

This skill does not:
- keep runtime memory inside the installed skill directory
- create a parallel memory system
- auto-promote, auto-demote, or auto-archive by default
- infer durable preferences from silence
- manage export, forget, or wipe flows by default
- modify external runtime state unless explicitly used in a live environment

## Non-Goals

These ideas existed in earlier versions or adjacent skills and are intentionally not part of the canonical workflow:
- repo-level hook scaffolding for other agents
- skill extraction as a default follow-up
- heavy archive / demotion systems
- broad promotion into every agent instruction file
- hidden cross-session state outside `.learnings/` and `~/self-improving/`

## Related Files

- [SKILL.md](/Users/evan/Documents/my-skills/self-improving/SKILL.md)
- [setup.md](/Users/evan/Documents/my-skills/self-improving/setup.md)
- [heartbeat-rules.md](/Users/evan/Documents/my-skills/self-improving/heartbeat-rules.md)
- [boundaries.md](/Users/evan/Documents/my-skills/self-improving/boundaries.md)
- [references/examples.md](/Users/evan/Documents/my-skills/self-improving/references/examples.md)

## Summary

If you remember only four things, remember these:

1. raw first
2. promote conservatively
3. promote to the smallest correct scope
4. never let the system silently invent durable rules
