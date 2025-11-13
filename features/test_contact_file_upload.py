from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.conf import settings
from django.urls import reverse


def contact_url():
    try:
        return reverse("contact")
    except Exception:
        # Fallback to known path
        return "/contact/"


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    ADMIN_CONTACT_EMAIL="admin@example.com",
    DEFAULT_FROM_EMAIL="support@example.com",
)
class ContactFileUploadTests(TestCase):
    def setUp(self):
        # Prepare URL
        self.contact_path = contact_url()

    def _init_captcha(self):
        # Trigger GET to initialize captcha session values
        self.client.get(self.contact_path)
        s = self.client.session
        # Prefer direct result if present; else compute from operands
        result = s.get("contact_captcha")
        if result is None:
            a = int(s.get("contact_captcha_a", 0))
            b = int(s.get("contact_captcha_b", 0))
            result = str(a + b)
        return str(result)

    def _post_contact(self, file_obj=None, content_type=None):
        captcha_value = self._init_captcha()
        data = {
            "name": "Test User",
            "email": "user@example.com",
            "subject": "Test Upload",
            "message": "Hello with attachment.",
            "captcha": captcha_value,
        }
        if file_obj is not None:
            data["attachment"] = file_obj
        return self.client.post(self.contact_path, data, follow=True)

    def _assert_admin_email_with_attachment(self, expected_filename: str, expected_mimetype_prefix: str):
        self.assertGreaterEqual(
            len(mail.outbox),
            2,
            msg="Expected two emails (admin + ack) to be sent.",
        )
        # Find admin and ack emails by recipient
        admin_email = next((m for m in mail.outbox if settings.ADMIN_CONTACT_EMAIL in m.to), None)
        ack_email = next((m for m in mail.outbox if "user@example.com" in m.to), None)
        self.assertIsNotNone(admin_email, msg="Admin email not found in outbox.")
        self.assertIsNotNone(ack_email, msg="Ack email not found in outbox.")

        # Reply-To should target the user
        self.assertEqual(
            admin_email.reply_to,
            ["user@example.com"],
            msg="Admin email Reply-To should be the user's address.",
        )

        # Attachment presence and tuple form (filename, content, mimetype)
        self.assertGreaterEqual(
            len(admin_email.attachments),
            1,
            msg="Admin email should include at least one attachment.",
        )
        filename, content, mimetype = admin_email.attachments[0]
        self.assertEqual(
            filename,
            expected_filename,
            msg=f"Attachment filename mismatch. Expected {expected_filename}, got {filename}.",
        )
        self.assertTrue(
            isinstance(content, (bytes, bytearray)) and len(content) > 0,
            msg="Attachment content should be non-empty bytes.",
        )
        self.assertTrue(
            mimetype.startswith(expected_mimetype_prefix),
            msg=f"Attachment mimetype should start with '{expected_mimetype_prefix}', got '{mimetype}'.",
        )

        # Multipart structure checks
        msg_obj = admin_email.message()
        self.assertTrue(
            msg_obj.is_multipart(),
            msg="Admin email should be multipart when an attachment is present.",
        )
        self.assertTrue(
            msg_obj.get_content_type().startswith("multipart"),
            msg=f"Admin email content type should be multipart*, got '{msg_obj.get_content_type()}'.",
        )

        # Ack email should not include attachments
        self.assertEqual(
            len(ack_email.attachments),
            0,
            msg="Ack email should not include attachments.",
        )

    def test_pdf_attachment_delivered_multipart(self):
        file_obj = SimpleUploadedFile(
            "hello.pdf",
            b"%PDF-1.4 test content\n",
            content_type="application/pdf",
        )
        response = self._post_contact(file_obj)
        self.assertEqual(response.status_code, 200, msg="Expected successful request after redirect.")
        self._assert_admin_email_with_attachment("hello.pdf", "application/pdf")

    def test_zero_byte_file_rejected_no_emails(self):
        file_obj = SimpleUploadedFile(
            "empty.pdf",
            b"",
            content_type="application/pdf",
        )
        response = self._post_contact(file_obj)
        # Form should re-render with errors (no redirect)
        self.assertEqual(response.status_code, 200, msg="Expected form re-render on validation error.")
        # Should surface attachment error
        form_errors = response.context["form"].errors if response.context and "form" in response.context else {}
        self.assertIn("attachment", form_errors, msg="Attachment field should have validation errors for zero-byte file.")
        self.assertEqual(len(mail.outbox), 0, msg="No emails should be sent when attachment validation fails.")
    def test_image_jpg_attachment_delivered(self):
        file_obj = SimpleUploadedFile(
            "photo.jpg",
            b"\xff\xd8\xff test jpeg bytes",
            content_type="image/jpg",  # common browser variant
        )
        response = self._post_contact(file_obj)
        self.assertEqual(response.status_code, 200, msg="Expected successful request after redirect.")
        self._assert_admin_email_with_attachment("photo.jpg", "image/")

    def test_octet_stream_fallback_pdf(self):
        file_obj = SimpleUploadedFile(
            "file.pdf",
            b"%PDF-1.4 test content\n",
            content_type="application/octet-stream",  # fallback scenario
        )
        response = self._post_contact(file_obj)
        self.assertEqual(response.status_code, 200, msg="Expected successful request after redirect.")
        self._assert_admin_email_with_attachment("file.pdf", "application/pdf")