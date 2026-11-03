from pathlib import Path

from app.processing.parsers.pdf_parser import extract_pdf_text
from app.processing.parsers.docx_parser import extract_docx_text
from app.processing.parsers.pptx_parser import extract_pptx_text
from app.processing.parsers.excel_parser import extract_excel_text


SUPPORTED_PARSERS = {
    ".pdf": extract_pdf_text,
    ".docx": extract_docx_text,
    ".pptx": extract_pptx_text,
    ".xlsx": extract_excel_text,
}


def extract_text(file_path: str) -> str:
    """
    Extract text from a supported document.
    """

    extension = Path(file_path).suffix.lower()

    parser = SUPPORTED_PARSERS.get(extension)

    if parser is None:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    return parser(file_path)