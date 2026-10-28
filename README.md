# open-research-agents

Agent skills for careful, verifiable research work. Each skill is a folder of
instructions, reference notes and small scripts that a coding agent (Claude Code, Codex and
others that support the open Agent Skills format) loads when a task calls for it.

The skills come from practice (building small-area public-health datasets from public and
restricted sources) and from the mistakes made along the way. They are meant to be improved by the people
who use them. See [Feedback](#feedback).

## Skills

| Skill | What it covers |
|---|---|
| [research-data-engineering](plugins/research-data-engineering/skills/research-data-engineering/SKILL.md) | Building datasets from scattered sources with provenance and publication dates; extracting tables and figures from PDF reports and validating them; keeping record-level data (PII/PHI) out of the agent's context with code-only access, synthetic stand-ins and locally hosted models. Includes a module for health and surveillance data (HIPAA identifiers, suppression, reporting delays) |

## How well it works

Each skill ships with test cases and a written evaluation: what it is tested on, and how Claude
Haiku, Sonnet and Opus perform with and without it. See
[research-data-engineering/EVALUATION.md](plugins/research-data-engineering/EVALUATION.md).
In short: with the skill all three models pass 97-100% of checks; without it the smaller models
expose protected records when asked to.

## Install

**Claude Code**

```
/plugin marketplace add openresearchagents/skills
/plugin install research-data-engineering@open-research-agents
```

**Other agents** (Codex, Cursor and others that read `SKILL.md` folders): copy
`plugins/research-data-engineering/skills/research-data-engineering/` into the agent's
skills directory (for Codex, `~/.agents/skills/` for all projects or `.agents/skills/` inside one repository; check your agent's docs).

## Privacy

The rule at the centre of these skills is to never put real records into an AI tool, only code. It
follows from how agents work (everything they read goes to the model provider) and is consistent
with privacy law and published public-health guidance; see the skill's
`references/related_guidance.md`.


Nothing in these skills sends data anywhere. They make no network calls and need no API keys. The
skills tell the agent to avoid reading protected records, but instructions are not enforcement:
use your agent's permission and sandbox settings as described in
`references/privacy_boundary.md`. This is not legal advice. Your data use agreements, IRB and
institutional policies decide what is allowed.

## Feedback

Please open an issue using one of the templates:

- **Field report**: you used a skill on a real task. What helped, what did not.
- **Wrong, outdated or risky advice**: a correction, ideally with a source.
- **Suggest a practice or a new skill**.

Never paste data, file contents or agent transcripts into an issue. Describe the task in general
terms.

## License

MIT
