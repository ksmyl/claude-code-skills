# nano-banana-pro

Claude Code skill for generating, editing, and iteratively refining images using Google's **Nano Banana Pro** (`gemini-3-pro-image-preview`) model.

## Features

- **Text-to-image generation** — create images from detailed text prompts
- **Natural-language editing** — modify existing images with plain English instructions
- **Multi-turn sessions** — iteratively refine images across multiple turns with full context preservation
- **Session persistence** — save and resume editing sessions later
- **Reference images** — up to 14 reference images for style/character consistency
- **Resolution control** — 512, 1K, 2K, or 4K output
- **Aspect ratios** — 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
- **Text rendering** — industry-leading text-in-image accuracy

## Setup

### 1. Get a Gemini API key

Visit [Google AI Studio](https://aistudio.google.com/) and create an API key.

> **Note:** Using this skill incurs charges on your Google account for Gemini API token usage. See [Google's pricing](https://ai.google.dev/pricing) for current rates.

### 2. Install as a Claude Code skill

```bash
cp -r nano-banana-pro ~/.claude/skills/nano-banana-pro
```

### 3. Configure API key

```bash
cd ~/.claude/skills/nano-banana-pro
cp .env.example .env
# Edit .env and paste your GEMINI_API_KEY
```

The key stays scoped to this skill. If `GEMINI_API_KEY` is already set as an environment variable, that works too.

### 4. Whitelist API domain (if sandboxed)

Add `generativelanguage.googleapis.com` to `allowedDomains` in `~/.claude/settings.json` if your Claude Code sandbox restricts network access.

## Usage in Claude Code

Just ask Claude to generate or edit images — the skill auto-triggers:

```
make me a 16:9 thumbnail for my youtube video about sourdough bread

edit ./photo.jpg to add dramatic lighting

make the text bolder   (continues session)
```

You can also invoke explicitly with `/nano-banana-pro <prompt>`.

## Standalone Usage

Scripts work independently from the skill directory:

```bash
cd ~/.claude/skills/nano-banana-pro

# Generate
uv run scripts/generate.py "A cat wearing a tiny hat" --resolution 4K --aspect-ratio 16:9

# Edit
uv run scripts/edit.py ./photo.jpg "Remove the background"

# Session (iterative)
uv run scripts/session.py "Design a logo for a coffee shop"
uv run scripts/session.py "Make the text bolder" --session-id <id>
uv run scripts/session.py --list-sessions
```

## Output

Images are saved to `./nano-banana-output/` in the working directory.

## Requirements

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) (dependencies managed via `pyproject.toml`, installed automatically)

## License

MIT
