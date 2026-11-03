from backend.app.processing.parsers.pdf_parser import extract_pdf_text

text = extract_pdf_text("uploads/sample.pdf")

print(text)