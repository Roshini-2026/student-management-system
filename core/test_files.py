import io
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Student
from .test_utils import make_course

User = get_user_model()
PHOTO_LIMIT = 2 * 1024 * 1024
DOC_LIMIT = 5 * 1024 * 1024


def png_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10)).save(buffer, "PNG")
    return buffer.getvalue()


def photo(name="photo.png", data=None):
    return SimpleUploadedFile(name, data or png_bytes(), content_type="image/png")


def pdf(name="doc.pdf", data=b"%PDF-1.4 test document"):
    return SimpleUploadedFile(name, data, content_type="application/pdf")


class UploadTestCase(TestCase):
    """Sends uploads to temporary folders, so tests never touch real files."""

    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", verbosity=0)
        cls.course = make_course()
        cls.users = {}
        for role in ("Staff", "Viewer"):
            user = User.objects.create_user(username=role.lower(), password="pass12345")
            user.groups.add(Group.objects.get(name=role))
            cls.users[role] = user

    def setUp(self):
        media = self.enterContext(tempfile.TemporaryDirectory())
        private = self.enterContext(tempfile.TemporaryDirectory())
        self.enterContext(override_settings(MEDIA_ROOT=media))
        field = Student._meta.get_field("supporting_document")
        storage = FileSystemStorage(location=private, base_url="/students/documents/")
        self.enterContext(patch.object(field, "storage", storage))
        self.media, self.private = Path(media), Path(private)
        self.client.force_login(self.users["Staff"])

    def student_data(self, **extra):
        return {
            "full_name": "Asha Rao", "email": "asha@example.com", "mobile_number": "9876543210",
            "gender": "F", "course": self.course.pk, "enrollment_status": "enrolled",
            "is_active": "on", **extra,
        }

    def create_with_files(self, **files):
        return self.client.post(reverse("student_create"), self.student_data(**files))

    def update_with_files(self, student, **files):
        return self.client.post(reverse("student_update", args=[student.pk]), self.student_data(**files))


class UploadTests(UploadTestCase):
    def test_valid_files_are_saved_with_safe_random_names(self):
        self.create_with_files(profile_photo=photo("../../my photo.PNG"), supporting_document=pdf("../evil.pdf"))
        student = Student.objects.get()
        self.assertRegex(student.profile_photo.name, r"^student_photos/[0-9a-f]{32}\.png$")
        self.assertRegex(student.supporting_document.name, r"^[0-9a-f]{32}\.pdf$")
        self.assertTrue(Path(student.profile_photo.path).is_file())
        self.assertTrue(Path(student.supporting_document.path).is_file())

    def test_documents_are_stored_outside_the_public_media_folder(self):
        self.create_with_files(supporting_document=pdf())
        document = Path(Student.objects.get().supporting_document.path)
        self.assertTrue(document.is_relative_to(self.private))
        self.assertFalse(document.is_relative_to(self.media))

    def assert_rejected(self, field, bad_files):
        for label, file in bad_files.items():
            with self.subTest(label):
                response = self.create_with_files(**{field: file})
                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context["form"].errors)
        self.assertEqual(Student.objects.count(), 0)

    def test_invalid_photos_are_rejected(self):
        self.assert_rejected("profile_photo", {
            "wrong extension": photo("photo.gif"),
            "not really an image": SimpleUploadedFile("fake.png", b"just text", content_type="image/png"),
            "too large": photo("big.png", png_bytes() + b"0" * PHOTO_LIMIT),
        })

    def test_invalid_documents_are_rejected(self):
        self.assert_rejected("supporting_document", {
            "wrong extension": SimpleUploadedFile("notes.txt", b"%PDF-1.4", content_type="text/plain"),
            "not really a pdf": SimpleUploadedFile("fake.pdf", b"just text", content_type="application/pdf"),
            "too large": pdf("big.pdf", b"%PDF-" + b"0" * DOC_LIMIT),
        })

    def test_replacing_a_file_deletes_the_old_one(self):
        self.create_with_files(profile_photo=photo())
        student = Student.objects.get()
        old_path = Path(student.profile_photo.path)
        self.update_with_files(student, profile_photo=photo("new.png"))
        student.refresh_from_db()
        self.assertFalse(old_path.exists())
        self.assertTrue(Path(student.profile_photo.path).is_file())

    def test_clearing_a_file_removes_it(self):
        self.create_with_files(supporting_document=pdf())
        student = Student.objects.get()
        old_path = Path(student.supporting_document.path)
        self.update_with_files(student, **{"supporting_document-clear": "on"})
        student.refresh_from_db()
        self.assertFalse(student.supporting_document)
        self.assertFalse(old_path.exists())

    def test_editing_without_new_files_keeps_the_existing_ones(self):
        self.create_with_files(profile_photo=photo(), supporting_document=pdf())
        student = Student.objects.get()
        self.update_with_files(student, full_name="Asha R")
        student.refresh_from_db()
        self.assertEqual(student.full_name, "Asha R")
        self.assertTrue(Path(student.profile_photo.path).is_file())
        self.assertTrue(Path(student.supporting_document.path).is_file())

    def test_deleting_a_student_deletes_their_files(self):
        self.create_with_files(profile_photo=photo(), supporting_document=pdf())
        student = Student.objects.get()
        paths = [Path(student.profile_photo.path), Path(student.supporting_document.path)]
        student.delete()
        self.assertFalse(any(path.exists() for path in paths))

    def test_bulk_delete_also_deletes_the_files(self):
        self.create_with_files(profile_photo=photo(), supporting_document=pdf())
        student = Student.objects.get()
        paths = [Path(student.profile_photo.path), Path(student.supporting_document.path)]
        Student.objects.all().delete()
        self.assertFalse(any(path.exists() for path in paths))
    
    def test_photo_is_shown_on_the_detail_page(self):
        self.create_with_files(profile_photo=photo())
        student = Student.objects.get()
        response = self.client.get(reverse("student_detail", args=[student.pk]))
        self.assertContains(response, student.profile_photo.url)


class DocumentAccessTests(UploadTestCase):
    def setUp(self):
        super().setUp()
        self.create_with_files(supporting_document=pdf())
        self.student = Student.objects.get()
        self.url = self.student.supporting_document.url

    def test_staff_can_download_the_document(self):
        response = self.client.get(self.url)
        content = b"".join(response.streaming_content)
        response.close()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, b"%PDF-1.4 test document")
        self.assertTrue(response["Content-Disposition"].startswith("attachment"))

    def test_viewer_cannot_download_the_document(self):
        self.client.force_login(self.users["Viewer"])
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_anonymous_user_is_sent_to_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}", fetch_redirect_response=False)

    def test_unknown_document_returns_404(self):
        self.assertEqual(self.client.get("/students/documents/nothing.pdf").status_code, 404)

    def test_document_missing_from_disk_returns_404(self):
        Path(self.student.supporting_document.path).unlink()
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_document_link_is_shown_only_to_staff(self):
        detail = reverse("student_detail", args=[self.student.pk])
        self.assertContains(self.client.get(detail), self.url)
        self.client.force_login(self.users["Viewer"])
        self.assertNotContains(self.client.get(detail), self.url)