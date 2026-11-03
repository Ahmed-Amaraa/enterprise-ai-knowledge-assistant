#from app.processing.parsers.docx_parser import extract_docx_text
from docx import Document

def extract_docx_text(file_path: str) -> str:
    """
    Extract all text from a DOCX document.
    """

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)


text = extract_docx_text("./app/tests/uploads/Chap.docx")

print(text)