---
name: self-improvement
description: "Injects a minimal self-improvement reminder during OpenClaw agent bootstrap"
metadata: {"openclaw":{"emoji":"🧠","events":["agent:bootstrap"]}}
---

# Self-Improvement Hook

This optional OpenClaw hook injects a small bootstrap reminder for the canonical two-layer workflow.

## What It Does

- fires on `agent:bootstrap`
- reminds the agent to use workspace `.learnings/` for raw capture
- reminds the agent to reserve `~/self-improving/` for durable promoted rules
- does not create runtime state

## Enable

```bash
openclaw hooks enable self-improvement
```
