from backend.app.processing.parsers.pptx_parser import extract_pptx_text

text = extract_pptx_text("uploads/example.pptx")

print(text)