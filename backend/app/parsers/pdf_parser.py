import fitz  # PyMuPDF


def extract_pdf_text(file_path: str) -> str:
    """
    Extract all text from a PDF document.
    """

    document = fitz.open(file_path)

    pages = []

    for page in document:
        pages.append(page.get_text())

    document.close()

    return "\n".join(pages)