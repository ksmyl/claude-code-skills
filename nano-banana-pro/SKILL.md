---
name: nano-banana-pro
description: Generate, edit, and iteratively refine images using Google Nano Banana Pro (Gemini 3 Pro Image). Use this skill whenever the user asks to create, generate, draw, design, or make any kind of image, photo, illustration, thumbnail, icon, logo, diagram, or visual asset. Also use when they want to edit, modify, touch up, or iterate on an existing image, or when they mention Nano Banana, Gemini image generation, or text-to-image. Even casual requests like "make me a picture of..." or "can you create a visual for..." should trigger this skill.
argument-hint: "[prompt or edit instruction]"
---

# Nano Banana Pro

This skill gives you the ability to generate and edit images through Google's Nano Banana Pro model (`gemini-3-pro-image-preview`). It supports three workflows: creating images from scratch, editing existing images with natural language, and iteratively refining images across multiple turns with session persistence.

## How to run scripts

Let `SKILL_DIR` be the directory containing this SKILL.md file. All scripts are invoked with this pattern:

```bash
UV_CACHE_DIR=/tmp/claude-1001/uv-cache \
UV_PROJECT_ENVIRONMENT=/tmp/claude-1001/nano-banana-venv \
uv run --frozen --project "$SKILL_DIR" \
  "$SKILL_DIR/scripts/<script>.py" <args>
```

This is important because the skill directory may be read-only (e.g., `~/.claude/skills/`). The env vars redirect the venv and cache to writable locations, and `--frozen` uses the shipped `uv.lock` without trying to write one. Using `--project` instead of `cd` keeps the user's working directory as CWD, so output files land where the user expects.

Dependencies are managed via `pyproject.toml` — `uv run` installs them automatically on first use.

## Which script to use

- **`scripts/generate.py`** — Create a new image from a text prompt. Supports `--resolution` (512, 1K, 2K, 4K) and `--aspect-ratio` (1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9).
- **`scripts/edit.py`** — Modify an existing image. Takes an image path and a natural-language edit instruction.
- **`scripts/session.py`** — Multi-turn iterative refinement. Creates a persistent session so the model remembers previous images and can apply incremental edits. Use `--session-id` to continue a previous session, or `--list-sessions` to see saved ones.

Each script prints the exact path of the saved image to stdout (e.g., `Image saved to: ./nano-banana-output/sunset_20260315_143022.png`). Capture this path from the script output — don't scan the output directory, since other sessions may be writing there concurrently.

## How to pick parameters

Don't ask the user for resolution and aspect ratio unless they care — infer from context instead. A YouTube thumbnail is 16:9, a phone wallpaper is 9:16, a portrait is 3:4, a logo is 1:1. Default to 2K resolution, which balances quality and cost.

For prompts, specificity helps enormously. "A golden retriever in autumn leaves, soft afternoon light, shallow depth of field" will produce much better results than "a dog". See [prompt-tips.md](prompt-tips.md) for more guidance to share with the user.

## After generating

Read the output image so you can see what the model produced and describe it to the user. This matters because the user can't always preview images in their terminal. Offer specific suggestions for refinement — "the lighting looks flat, want me to try adding more contrast?" is more helpful than "want me to change anything?"

If the user wants changes, switch to `scripts/session.py` to iterate. Tell them the session ID so they can resume later, even in a different conversation.

## When things go wrong

- **No image returned** — usually a content policy issue, suggest rephrasing the prompt.
- **GEMINI_API_KEY not set** — the scripts load it from a `.env` file in the skill directory, or from the environment. Guide the user to copy `.env.example` to `.env` and add their key (get one at https://aistudio.google.com/).
- For detailed API patterns and code examples, see [api-reference.md](api-reference.md).
