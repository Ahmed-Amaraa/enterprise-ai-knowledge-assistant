from app.parsers.excel_parser import extract_excel_text

text = extract_excel_text("uploads/example.xlsx")

print(text)