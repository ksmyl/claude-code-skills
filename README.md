# claude-code-skills

A collection of custom [Claude Code](https://claude.com/claude-code) skills.

## Skills

| Skill | Description | Platform | Setup after install |
|---|---|---|---|
| [nano-banana-pro](nano-banana-pro/) | Generate, edit, and iteratively refine images using Google Nano Banana Pro | All (Python 3.11+) | Copy `.env.example` to `.env` in `~/.claude/skills/nano-banana-pro/` and add your `GEMINI_API_KEY` (get one at [aistudio.google.com](https://aistudio.google.com/)), whitelist `generativelanguage.googleapis.com` in sandbox |

## Installation

Copy a skill directory to `~/.claude/skills/` to make it available in all Claude Code sessions:

```bash
cp -r <skill-name> ~/.claude/skills/<skill-name>
```

Or copy to `.claude/skills/` inside a specific project for project-scoped access.

Check the "Setup after install" column — some skills need API keys or sandbox configuration.

## Requirements

- [Claude Code](https://claude.com/claude-code)
- [uv](https://docs.astral.sh/uv/) — skills use `uv` for dependency management
- Python >= 3.11

## Structure

Each skill follows the [Agent Skills](https://agentskills.io/specification) open standard:

```
skill-name/
├── SKILL.md           # Required — frontmatter + instructions for Claude
├── pyproject.toml     # Dependencies managed by uv
├── uv.lock            # Shipped for reproducible installs in read-only environments
├── .env.example       # API key template (if the skill needs one)
├── scripts/           # Executable Python scripts
├── references/        # Documentation Claude reads on demand
└── README.md          # Human-facing setup and usage docs
```

## License

MIT
