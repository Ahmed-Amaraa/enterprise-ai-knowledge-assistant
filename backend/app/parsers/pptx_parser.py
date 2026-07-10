from pptx import Presentation


def extract_pptx_text(file_path: str) -> str:
    """
    Extract all text from a PowerPoint presentation.
    """

    presentation = Presentation(file_path)

    slides = []

    for slide in presentation.slides:

        for shape in slide.shapes:

            if hasattr(shape, "text"):

                text = shape.text.strip()

                if text:
                    slides.append(text)

    return "\n".join(slides)