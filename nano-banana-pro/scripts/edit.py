#!/usr/bin/env python3
"""Nano Banana Pro — image editing script.

Edit existing images using natural-language instructions.
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load .env from the skill directory (next to scripts/)
_skill_dir = Path(__file__).resolve().parent.parent
load_dotenv(_skill_dir / ".env")


def edit_image(
    image_path: str,
    instruction: str,
    output_dir: str = "./nano-banana-output",
    filename: str | None = None,
    resolution: str = "2K",
) -> str:
    """Edit an existing image using a natural-language instruction.

    Returns the path to the saved edited image, or empty string on failure.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    src = Path(image_path)
    if not src.exists():
        print(f"ERROR: Image not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    image_bytes = src.read_bytes()
    suffix = src.suffix.lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
    mime = mime_map.get(suffix, "image/png")

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[
            types.Content(
                parts=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime),
                    types.Part.from_text(text=instruction),
                ],
            ),
        ],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                image_size=resolution,
            ),
        ),
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if filename is None:
        slug = re.sub(r"[^a-z0-9_]+", "_", "_".join(instruction.lower().split()[:4]))[:60]
        filename = f"edit_{slug}_{timestamp}.png"
    else:
        filename = Path(filename).name

    if not response.candidates:
        print("ERROR: No candidates returned — the prompt may have been blocked.", file=sys.stderr)
        return ""

    saved_path = None
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            save_to = out / filename
            save_to.write_bytes(part.inline_data.data)
            saved_path = str(save_to)
            print(f"Edited image saved to: {saved_path}")
        elif part.text is not None:
            print(f"Model notes: {part.text}")

    if saved_path is None:
        print("WARNING: No image was returned by the model.", file=sys.stderr)

    return saved_path or ""


def main():
    parser = argparse.ArgumentParser(description="Edit image with Nano Banana Pro")
    parser.add_argument("image", help="Path to the image to edit")
    parser.add_argument("instruction", help="Natural-language edit instruction")
    parser.add_argument("--output-dir", default="./nano-banana-output", help="Output directory")
    parser.add_argument("--filename", default=None, help="Output filename (auto-generated if omitted)")
    parser.add_argument(
        "--resolution",
        default="2K",
        choices=["512", "1K", "2K", "4K"],
        help="Image resolution (default: 2K)",
    )
    args = parser.parse_args()
    edit_image(args.image, args.instruction, args.output_dir, args.filename, args.resolution)


if __name__ == "__main__":
    main()
