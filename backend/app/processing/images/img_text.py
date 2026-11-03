from pathlib import Path
from PIL import Image
import pytesseract

from google import genai
from google.genai import types
from pathlib import Path


client = genai.Client()





def extract_text_from_image(image_path: str) -> str:
    """
    Extracts text from an image using OCR (Optical Character Recognition).

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: Extracted text from the image.
    """
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    try:
        image = Image.open(image_path)

        text = pytesseract.image_to_string(image)

        return text.strip()

    except Exception as e:
        raise RuntimeError(
            f"Failed to extract text from image: {image_path}"
        ) from e