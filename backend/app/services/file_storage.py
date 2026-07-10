import os
import uuid
from fastapi import UploadFile

UPLOAD_DIR = "uploads"


def save_file(file: UploadFile) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_extension = file.filename.split(".")[-1]
    file_id = str(uuid.uuid4())
    file_path = f"{UPLOAD_DIR}/{file_id}.{file_extension}"

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path