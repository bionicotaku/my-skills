# Security Boundaries

These boundaries apply to both storage layers:
- raw capture in `~/.openclaw/workspace/.learnings/`
- promoted memory in `~/self-improving/`

## Never Store

| Category | Examples | Why |
|----------|----------|-----|
| Credentials | Passwords, API keys, tokens, SSH keys | Security breach risk |
| Financial | Card numbers, bank accounts, crypto seeds | Fraud risk |
| Medical | Diagnoses, medications, conditions | Privacy risk |
| Biometric | Voiceprints, behavioral fingerprints | Identity theft risk |
| Third-party personal data | Private details about other people | No consent |
| Location patterns | Home address, travel routines, exact schedules | Physical safety risk |
| Access patterns | Internal system access, privileged routes, escalation clues | Security abuse risk |

## Store With Caution

| Category | Rules |
|----------|-------|
| Work context | Keep only what improves execution; do not over-retain stale project detail |
| Emotional state | Only if explicitly relevant and explicitly shared |
| Relationships | Roles only when needed for task context |
| Schedules | General patterns only, not exact private timing |

## Transparency Rules

1. If a stored rule affects behavior, it should be visible in the relevant layer.
2. The path from raw capture to promoted rule should stay understandable.
3. Actions based on stored guidance should be explainable.
4. Do not keep hidden shadow state outside the documented layers.

## Red Flags

Stop if you find yourself:
- storing something "just in case"
- inferring a durable preference from silence
- carrying private context across unrelated scopes
- retaining third-party information that is not yours to keep
- writing sensitive runtime state into installed skill folders

## Consent Model

| Data Type | Consent Level |
|-----------|---------------|
| Explicit corrections | Implied by the correction |
| Durable preferences | Explicit confirmation or strong repeated evidence |
| Domain or project rules | Clear repeated evidence or clear scope |
| Cross-session behavioral patterns | Explicit opt-in or clear long-term confirmation |
