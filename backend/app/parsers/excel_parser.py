from openpyxl import load_workbook


def extract_excel_text(file_path: str) -> str:
    """
    Extract all text from an Excel workbook.
    """

    workbook = load_workbook(
        filename=file_path,
        data_only=True
    )

    rows = []

    for sheet in workbook.worksheets:

        rows.append(f"Sheet: {sheet.title}")

        for row in sheet.iter_rows(values_only=True):

            values = []

            for cell in row:

                if cell is not None:
                    values.append(str(cell))

            if values:
                rows.append(" | ".join(values))

    return "\n".join(rows)