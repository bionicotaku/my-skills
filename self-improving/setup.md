# Setup and Recovery

Use this file to align an OpenClaw workspace with the canonical two-layer self-improvement model without touching existing runtime data.

## Runtime Paths

Expected runtime locations:

```text
~/.openclaw/workspace/.learnings/
~/self-improving/
```

`~/.openclaw/workspace/.learnings/` is the raw layer.
`~/self-improving/` is the promoted layer.

Do not create runtime memory or state inside the installed skill directory.

## Workspace Guidance

Align these files with the same routing model:

### `AGENTS.md`

Make sure it says, in effect:
- factual continuity stays in workspace memory files
- raw failures, tentative lessons, and missing capabilities go to `.learnings/`
- durable rules and preferences go to `~/self-improving/`
- promotion from `.learnings/` is conservative and auditable

### `SOUL.md`

Make sure it says, in effect:
- load `~/self-improving/memory.md` before non-trivial work
- load only the smallest matching domain or project files
- write raw incidents to `.learnings/`
- promote only confirmed or repeated patterns

### `HEARTBEAT.md`

Keep it minimal. Point it at:
- this skill's `heartbeat-rules.md`
- `~/self-improving/heartbeat-state.md`

Example:

```markdown
## Self-Improving Check

- Read `/Users/evan/.openclaw/workspace/skills/self-improving/heartbeat-rules.md`
- Use `~/self-improving/heartbeat-state.md` for last-run markers and action notes
- If no file inside `~/self-improving/` changed since the last reviewed change, return `HEARTBEAT_OK`
```

## Hook Recovery

If the OpenClaw hook is missing and you want the bootstrap reminder back:

```bash
cp -r hooks/openclaw ~/.openclaw/hooks/self-improvement
openclaw hooks enable self-improvement
```

This hook is optional. It should only inject a reminder to use the two-layer workflow. It should not create runtime state.

## Recovery Checklist

If behavior drifts, verify these facts in order:

1. `.learnings/` exists under `~/.openclaw/workspace/`
2. `~/self-improving/` exists and contains promoted memory files
3. `AGENTS.md`, `SOUL.md`, and `HEARTBEAT.md` still describe the same routing model
4. the optional hook, if installed, still points to the canonical reminder logic

## Do Not Reintroduce

Do not bring back:
- skill-directory runtime logs or memory files
- repo-level hook scaffolding for other agent ecosystems
- automatic promotion from raw incidents into long-term memory
- default extraction or publication workflows
