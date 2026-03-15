# Nano Banana Pro — API Reference

## Model

- **Model ID**: `gemini-3-pro-image-preview`
- **Provider**: Google DeepMind (Gemini family)
- **API endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent`
- **Auth**: `GEMINI_API_KEY` environment variable

## Python SDK Setup

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
```

## Generation Config

```python
config = types.GenerateContentConfig(
    response_modalities=["TEXT", "IMAGE"],  # Required for image output
    image_config=types.ImageConfig(
        aspect_ratio="1:1",    # 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
        image_size="2K",       # 512, 1K, 2K, 4K
    ),
)
```

## Text-to-Image

```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="A watercolor painting of a mountain lake",
    config=config,
)

for part in response.candidates[0].content.parts:
    if part.inline_data is not None:
        Path("output.png").write_bytes(part.inline_data.data)
    elif part.text is not None:
        print(part.text)
```

## Image Editing

Send the source image + edit instruction as multimodal content:

```python
image_bytes = Path("photo.jpg").read_bytes()

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        types.Content(parts=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            types.Part.from_text(text="Remove the background and add dramatic lighting"),
        ]),
    ],
    config=config,
)
```

## Multi-Turn Session (Iterative Editing)

Use the chat interface to maintain context across turns:

```python
chat = client.chats.create(
    model="gemini-3-pro-image-preview",
    config=config,
    history=[],  # or load from saved session
)

response1 = chat.send_message("Design a poster for a tech conference")
# ... extract and save image ...

response2 = chat.send_message("Make the title larger and change background to dark blue")
# The model remembers the previous image and applies edits

# Save history for later
history = chat.get_history()
```

## Reference Images (Style/Character Consistency)

Include up to 14 reference images alongside the prompt:

```python
parts = []
for ref_path in reference_image_paths:
    ref = Path(ref_path)
    mime = "image/png" if ref.suffix.lower() == ".png" else "image/jpeg"
    parts.append(types.Part.from_bytes(data=ref.read_bytes(), mime_type=mime))

parts.append(types.Part.from_text(text="Generate a new image in this style"))

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[types.Content(parts=parts)],
    config=config,
)
```

## Supported MIME Types

- Input: `image/png`, `image/jpeg`, `image/webp`, `image/heic`, `image/heif`
- Output: `image/png`, `image/jpeg`

## Pricing (approximate)

- 2K image: ~$0.12
- 4K image: ~$0.24
