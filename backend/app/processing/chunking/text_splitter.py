from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 100,
) -> list[str]:
    """
    Split text into overlapping chunks while preserving as much
    document structure as possible.

    Args:
        text: Cleaned document text.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Number of overlapping characters.

    Returns:
        List of text chunks.
    """

    if not text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",   # paragraphs
            "\n",     # lines
            ". ",     # sentences
            " ",      # words
            ""        # characters (last resort)
        ],
        length_function=len,
        is_separator_regex=False,
    )

    return splitter.split_text(text)