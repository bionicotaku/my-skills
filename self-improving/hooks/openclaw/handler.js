/**
 * Minimal OpenClaw self-improvement hook.
 *
 * Injects a reminder for the canonical two-layer workflow during bootstrap.
 */

const REMINDER_CONTENT = `
## Self-Improvement Reminder

Use the two-layer workflow:

- Raw incidents, tentative lessons, and missing capabilities -> workspace \`.learnings/\`
- Durable confirmed rules and scoped long-term guidance -> \`~/self-improving/\`

Promotion is conservative:
- first occurrence stays raw
- ambiguous scope stays raw
- only confirmed or repeated patterns get promoted
`.trim();

const handler = async (event) => {
  if (!event || typeof event !== 'object') {
    return;
  }

  if (event.type !== 'agent' || event.action !== 'bootstrap') {
    return;
  }

  if (!event.context || typeof event.context !== 'object') {
    return;
  }

  const sessionKey = event.sessionKey || '';
  if (sessionKey.includes(':subagent:')) {
    return;
  }

  if (Array.isArray(event.context.bootstrapFiles)) {
    event.context.bootstrapFiles.push({
      path: 'SELF_IMPROVEMENT_REMINDER.md',
      content: REMINDER_CONTENT,
      virtual: true,
    });
  }
};

module.exports = handler;
module.exports.default = handler;
