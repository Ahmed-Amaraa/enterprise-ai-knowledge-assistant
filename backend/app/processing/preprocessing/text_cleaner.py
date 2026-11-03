import re


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted document text before chunking.

    Steps:
    - Normalize line endings
    - Remove tabs
    - Remove invisible/control characters
    - Collapse multiple spaces
    - Collapse excessive blank lines
    - Strip leading/trailing whitespace
    """

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Replace tabs with spaces
    text = text.replace("\t", " ")

    # Remove form feed (common in PDFs)
    text = text.replace("\f", "\n")

    # Remove non-printable characters
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    # Collapse multiple spaces
    text = re.sub(r"[ ]{2,}", " ", text)

    # Remove spaces around newlines
    text = re.sub(r" *\n *", "\n", text)

    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove leading/trailing spaces
    text = text.strip()

    return text