import uuid
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


def get_private_storage():
    """Storage for private documents: a folder outside MEDIA_ROOT, so it has no public URL."""
    return FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT, base_url="/students/documents/")


def _random_name(folder, filename):
    """Ignore the client's filename. Keep only its extension, in lower case."""
    return f"{folder}{uuid.uuid4().hex}{Path(filename).suffix.lower()}"


def photo_path(instance, filename):
    return _random_name("student_photos/", filename)


def document_path(instance, filename):
    return _random_name("", filename)


@deconstructible
class MaxFileSize:
    """Rejects a new upload bigger than the given number of megabytes."""

    def __init__(self, megabytes):
        self.megabytes = megabytes

    def __call__(self, file):
        if getattr(file, "_committed", False):
            return  # already stored earlier, nothing new to check
        if file.size > self.megabytes * 1024 * 1024:
            raise ValidationError(f"The file is too large. The maximum size is {self.megabytes} MB.")

    def __eq__(self, other):
        return isinstance(other, MaxFileSize) and self.megabytes == other.megabytes


def validate_pdf_content(file):
    """A real PDF starts with '%PDF-'. This catches files that only have a .pdf name."""
    if getattr(file, "_committed", False):
        return
    header = file.read(5)
    file.seek(0)  # go back to the start so the file can still be saved
    if header != b"%PDF-":
        raise ValidationError("The file is not a valid PDF.")