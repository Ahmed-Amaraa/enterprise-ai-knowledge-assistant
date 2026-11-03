import fitz
from pathlib import Path
from docx import Document


def extract_docx_images(docx_path: str, output_dir: str) -> list:
    """
    Extract embedded images from a DOCX document.
    """
    doc = Document(docx_path)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    images = []

    for relationship in doc.part.rels.values():

        if "image" not in relationship.reltype:
            continue

        image_part = relationship.target_part

        image_name = Path(image_part.partname).name
        image_path = output_dir / image_name

        with open(image_path, "wb") as f:
            f.write(image_part.blob)

        images.append({
            "path": str(image_path),
            "name": image_name,
        })

    return images


def extract_pdf_images(pdf_path: str, output_dir: str) -> list:
    """
    Extract images from a PDF document.
    """
    doc = fitz.open(pdf_path)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    images = []

    for page_number, page in enumerate(doc):
        for image_index, image in enumerate(page.get_images(full=True)):
            xref = image[0]

            image_data = doc.extract_image(xref)

            image_bytes = image_data["image"]
            extension = image_data["ext"]

            image_path = (
                output_dir
                / f"page_{page_number + 1}_image_{image_index + 1}.{extension}"
            )

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            images.append({
                "path": str(image_path),
                "page": page_number + 1,
                "image_index": image_index + 1,
            })

    doc.close()

    return images


SUPPORTED_PARSERS = {
    ".pdf": extract_pdf_images,
    ".docx": extract_docx_images,
}


def extract_images(file_path: str, output_dir: str) -> list:
    """
    Extract images from a supported document.
    """
    extension = Path(file_path).suffix.lower()

    parser = SUPPORTED_PARSERS.get(extension)

    if parser is None:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    return parser(file_path, output_dir)


def process_images(images: list) -> list:
    """
    Validate extracted images and return their paths.
    """
    processed_images = []

    for image in images:
        file_path = image.get("path")

        if not file_path:
            continue

        if not Path(file_path).exists():
            continue

        processed_images.append(image)

    return processed_images