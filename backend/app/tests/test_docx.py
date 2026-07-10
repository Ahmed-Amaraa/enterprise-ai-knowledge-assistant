from app.parsers.docx_parser import extract_docx_text

text = extract_docx_text("uploads/example.docx")

print(text)