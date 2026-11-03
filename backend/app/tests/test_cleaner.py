from backend.app.processing.preprocessing.text_cleaner import clean_text


raw_text = """

Python     is      awesome.



It\tis widely used.



\fFastAPI    is modern.

"""

cleaned = clean_text(raw_text)

print(cleaned)