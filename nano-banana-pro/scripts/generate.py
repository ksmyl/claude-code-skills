#!/usr/bin/env python3
"""Nano Banana Pro — image generation script.

Generate images from text prompts using Google's Gemini 3 Pro Image model.
"""

import argparse
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


def generate_image(
    prompt: str,
    output_dir: str = "./nano-banana-output",
    filename: str | None = None,
    aspect_ratio: str = "1:1",
    resolution: str = "2K",
) -> str:
    """Generate an image from a text prompt and save it.

    Returns the path to the saved image, or empty string on failure.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=resolution,
            ),
        ),
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if filename is None:
        slug = "_".join(prompt.lower().split()[:5]).replace("/", "-")
        filename = f"{slug}_{timestamp}.png"

    saved_path = None
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            save_to = out / filename
            save_to.write_bytes(part.inline_data.data)
            saved_path = str(save_to)
            print(f"Image saved to: {saved_path}")
        elif part.text is not None:
            print(f"Model notes: {part.text}")

    if saved_path is None:
        print("WARNING: No image was returned by the model.", file=sys.stderr)

    return saved_path or ""


def main():
    parser = argparse.ArgumentParser(description="Generate image with Nano Banana Pro")
    parser.add_argument("prompt", help="Text prompt for image generation")
    parser.add_argument("--output-dir", default="./nano-banana-output", help="Output directory")
    parser.add_argument("--filename", default=None, help="Output filename (auto-generated if omitted)")
    parser.add_argument(
        "--aspect-ratio",
        default="1:1",
        choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
        help="Image aspect ratio (default: 1:1)",
    )
    parser.add_argument(
        "--resolution",
        default="2K",
        choices=["512", "1K", "2K", "4K"],
        help="Image resolution (default: 2K)",
    )
    args = parser.parse_args()
    generate_image(args.prompt, args.output_dir, args.filename, args.aspect_ratio, args.resolution)


if __name__ == "__main__":
    main()
