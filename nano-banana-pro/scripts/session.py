#!/usr/bin/env python3
"""Nano Banana Pro — multi-turn session for iterative image editing.

Maintains conversation history so the model can refine images across multiple turns.
Sessions are saved to disk and can be resumed later.
"""

import argparse
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load .env from the skill directory (next to scripts/)
_skill_dir = Path(__file__).resolve().parent.parent
load_dotenv(_skill_dir / ".env")

SESSION_DIR = Path("./nano-banana-output/.sessions")


def save_session(session_id: str, history: list) -> Path:
    """Save conversation history to a session file."""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    session_file = SESSION_DIR / f"{session_id}.json"
    serializable = []
    for msg in history:
        parts_data = []
        for part in msg.parts:
            if part.text is not None:
                parts_data.append({"type": "text", "text": part.text})
            elif part.inline_data is not None:
                parts_data.append(
                    {
                        "type": "image",
                        "mime_type": part.inline_data.mime_type,
                        "data": base64.b64encode(part.inline_data.data).decode(),
                    }
                )
        serializable.append({"role": msg.role, "parts": parts_data})
    session_file.write_text(json.dumps(serializable, indent=2))
    print(f"Session saved: {session_file}")
    return session_file


def load_session(session_id: str) -> list | None:
    """Load a previously saved session. Returns None if not found."""
    session_file = SESSION_DIR / f"{session_id}.json"
    if not session_file.exists():
        return None
    data = json.loads(session_file.read_text())
    history = []
    for msg in data:
        parts = []
        for p in msg["parts"]:
            if p["type"] == "text":
                parts.append(types.Part.from_text(text=p["text"]))
            elif p["type"] == "image":
                parts.append(
                    types.Part.from_bytes(
                        data=base64.b64decode(p["data"]),
                        mime_type=p["mime_type"],
                    )
                )
        history.append(types.Content(role=msg["role"], parts=parts))
    print(f"Session loaded: {session_file} ({len(history)} turns)")
    return history


def list_sessions() -> list[dict]:
    """List all saved sessions with metadata."""
    if not SESSION_DIR.exists():
        return []
    sessions = []
    for f in sorted(SESSION_DIR.glob("*.json")):
        data = json.loads(f.read_text())
        turn_count = len(data) // 2
        # Extract first user prompt as summary
        first_prompt = ""
        for msg in data:
            if msg["role"] == "user":
                for part in msg["parts"]:
                    if part["type"] == "text":
                        first_prompt = part["text"][:80]
                        break
                break
        sessions.append(
            {
                "id": f.stem,
                "turns": turn_count,
                "first_prompt": first_prompt,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            }
        )
    return sessions


def session_turn(
    prompt: str,
    session_id: str | None = None,
    output_dir: str = "./nano-banana-output",
    resolution: str = "2K",
    aspect_ratio: str = "1:1",
) -> tuple[str | None, str]:
    """Execute one turn of a multi-turn image session.

    Returns (saved_image_path, session_id).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    if session_id is None:
        session_id = datetime.now().strftime("session_%Y%m%d_%H%M%S")

    history = load_session(session_id) or []

    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=resolution,
        ),
    )

    chat = client.chats.create(
        model="gemini-3-pro-image-preview",
        config=config,
        history=history,
    )

    response = chat.send_message(prompt)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    turn_num = len(history) // 2 + 1

    saved_path = None
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            filename = f"{session_id}_turn{turn_num}_{timestamp}.png"
            save_to = out / filename
            save_to.write_bytes(part.inline_data.data)
            saved_path = str(save_to)
            print(f"Image saved to: {saved_path}")
        elif part.text is not None:
            print(f"Model notes: {part.text}")

    save_session(session_id, chat.get_history())

    if saved_path is None:
        print("WARNING: No image was returned by the model.", file=sys.stderr)

    return saved_path, session_id


def main():
    parser = argparse.ArgumentParser(description="Iterative image session with Nano Banana Pro")
    parser.add_argument("prompt", nargs="?", help="Prompt or edit instruction")
    parser.add_argument("--session-id", default=None, help="Session ID to continue (omit for new session)")
    parser.add_argument("--list-sessions", action="store_true", help="List all saved sessions")
    parser.add_argument("--output-dir", default="./nano-banana-output", help="Output directory")
    parser.add_argument(
        "--resolution",
        default="2K",
        choices=["512", "1K", "2K", "4K"],
        help="Image resolution (default: 2K)",
    )
    parser.add_argument(
        "--aspect-ratio",
        default="1:1",
        choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
        help="Image aspect ratio (default: 1:1)",
    )
    args = parser.parse_args()

    if args.list_sessions:
        sessions = list_sessions()
        if sessions:
            print(f"{'ID':<35} {'Turns':>5}  {'Modified':<17}  First Prompt")
            print("-" * 100)
            for s in sessions:
                print(f"{s['id']:<35} {s['turns']:>5}  {s['modified']:<17}  {s['first_prompt']}")
        else:
            print("No saved sessions found.")
        sys.exit(0)

    if not args.prompt:
        parser.error("prompt is required unless --list-sessions is used")

    path, sid = session_turn(
        args.prompt,
        args.session_id,
        args.output_dir,
        args.resolution,
        args.aspect_ratio,
    )
    print(f"Session ID: {sid}")
    if path:
        print(f"Use --session-id {sid} to continue this session.")


if __name__ == "__main__":
    main()
