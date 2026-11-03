import json
import mimetypes
from pathlib import Path

from google import genai
from google.genai import types

from app.core.config import GEMINI_API_KEY
from app.processing.images.parser_process import extract_images, process_images


IMAGE_DESCRIPTION_PROMPT = """
You are an image analysis component of an Enterprise AI Knowledge Assistant.

Determine whether the provided image contains IMPORTANT INFORMATION that should
be added to a document knowledge base for semantic search and RAG.

Useful images include diagrams, flowcharts, meaningful tables or charts,
relevant screenshots, technical drawings, process diagrams, organizational
structures, informative maps, important text, and useful infographics.

Not useful images include decorative photos, portraits, generic office or event
photos, standalone logos, backgrounds, and images with no meaningful information.

Rules:
- Do not describe an image merely because it exists.
- If the image is not useful, return an empty text and util false.
- If it is useful, provide a clear, factual description of visible information.
- Include important visible text when appropriate.
- Do not invent information.
- Return only valid JSON with exactly two keys: text and util.

For a useful image:
{"text": "description of the useful information", "util": true}

For a useless image:
{"text": "", "util": false}
"""


class ImageDescriptionService:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def describe_image(self, image_path: str) -> dict[str, str | bool]:
        try:
            path = Path(image_path)
            mime_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"

            with path.open("rb") as image_file:
                response = self.client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents=[
                        types.Part.from_bytes(
                            data=image_file.read(),
                            mime_type=mime_type,
                        ),
                        IMAGE_DESCRIPTION_PROMPT,
                    ],
                )

            result = json.loads(response.text.strip())
            if set(result) != {"text", "util"}:
                raise ValueError("Gemini returned an invalid image description")
            if not isinstance(result["text"], str) or not isinstance(result["util"], bool):
                raise ValueError("Gemini returned invalid image description types")
            if not result["util"]:
                result["text"] = ""
            return result
        except Exception:
            return {"text": "", "util": False}

    def describe_document_images(self, file_path: str) -> str:
        extension = Path(file_path).suffix.lower()
        if extension not in {".pdf", ".docx"}:
            return ""

        image_dir = Path(file_path).with_name(f"{Path(file_path).stem}_images")
        try:
            images = process_images(extract_images(file_path, str(image_dir)))
        except (OSError, ValueError):
            return ""

        descriptions = []
        for image in images:
            result = self.describe_image(image["path"])
            if not result["util"] or not result["text"]:
                continue

            location = ""
            if image.get("page"):
                location = f" on page {image['page']}"
            descriptions.append(f"Image description{location}:\n{result['text']}")

        return "\n\n".join(descriptions)