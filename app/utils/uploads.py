from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename


def save_resume(file_storage, student_id):
    original = secure_filename(file_storage.filename or "")
    extension = Path(original).suffix.lower()
    if extension != ".pdf":
        raise ValueError("Only PDF files are allowed.")

    filename = f"student-{student_id}-{uuid4().hex}.pdf"
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination = upload_dir / filename
    file_storage.save(destination)
    return filename
