# Examples

These examples show how the two-layer model should be used.

## Raw Layer: Failure

Append to `~/.openclaw/workspace/.learnings/ERRORS.md`:

```markdown
## [ERR-20260415-001] api_timeout

### Summary
Checkout API timed out after 30 seconds

### Context
- command: POST /api/checkout
- task: payment flow validation
- reproducible: yes

### Suggested Follow-Up
Add retry logic or verify upstream timeout policy.
```

Reason:
- this is a raw incident
- it should not become long-term memory on first occurrence

## Raw Layer: Tentative Lesson

Append to `~/.openclaw/workspace/.learnings/LEARNINGS.md`:

```markdown
## [LRN-20260415-002] correction

### Summary
User prefers concise close-out messages for routine code changes

### Context
User corrected the response style after a routine implementation task.

### Status
tentative
```

Reason:
- first correction stays raw unless the human clearly says it is a lasting rule

## Promoted Layer: Durable Global Rule

Append to `~/self-improving/memory.md`:

```markdown
## Response style
- Keep routine implementation close-outs concise unless the human asks for depth.
```

Promote only if:
- the human explicitly says this is their standing preference, or
- the same lesson is confirmed repeatedly

## Promoted Layer: Domain Rule

Append to `~/self-improving/domains/agent-workflow.md`:

```markdown
## Raw vs promoted routing
- First failures and ambiguous lessons stay in workspace `.learnings/`.
- Durable workflow rules move to `~/self-improving/` only after confirmation or strong repetition.
```

Use this when:
- the lesson is clearly about agent workflow as a reusable domain pattern

## Promotion Trace

Keep promotions auditable.

Example trace:

1. First failure is logged to `~/.openclaw/workspace/.learnings/ERRORS.md`
2. A similar failure recurs and a reusable mitigation is logged to `~/.openclaw/workspace/.learnings/LEARNINGS.md`
3. The same mitigation works across multiple tasks
4. The durable rule is promoted into the smallest correct target under `~/self-improving/`

Example promoted entry:

```markdown
## API client regeneration
- After OpenAPI changes, regenerate the client before type-checking.
- Promoted from repeated raw incidents in workspace `.learnings/`.
```

This keeps the raw source, the confirmation path, and the promoted rule distinct.
