import json

from django.test import TestCase

from core.models import EmailDraft
from core.tests.helpers import EmailDraftAPITestMixin


class EmailDraftAPIVersionTests(EmailDraftAPITestMixin, TestCase):
    def test_post_generates_next_version_per_contact_and_task(self):
        response = self.client.post(
            "/api/email-drafts/",
            data=json.dumps(
                {
                    "contact": str(self.contact_two.pk),
                    "task": str(self.task.pk),
                    "subject": "Second for Grace",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["version"], 2)

        other_task_response = self.client.post(
            "/api/email-drafts/",
            data=json.dumps(
                {
                    "contact": str(self.contact_two.pk),
                    "task": str(self.other_task.pk),
                    "subject": "First for Grace in another task",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(other_task_response.status_code, 201)
        self.assertEqual(other_task_response.json()["version"], 1)

    def test_post_preserves_sent_status_on_older_versions(self):
        EmailDraft.objects.filter(pk=self.contact_one_old.pk).update(
            status=EmailDraft.Status.SENT
        )

        response = self.client.post(
            "/api/email-drafts/",
            data=json.dumps(
                {
                    "contact": str(self.contact_one.pk),
                    "task": str(self.task.pk),
                    "subject": "Newest after sent",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["version"], 3)
        self.assertEqual(response.json()["status"], EmailDraft.Status.SCHEDULED)

        self.contact_one_old.refresh_from_db()
        self.contact_one_latest.refresh_from_db()
        self.assertEqual(self.contact_one_old.status, EmailDraft.Status.SENT)
        self.assertEqual(self.contact_one_latest.status, EmailDraft.Status.DRAFT)

    def test_post_rejects_supplied_version(self):
        response = self.client.post(
            "/api/email-drafts/",
            data=json.dumps(
                {
                    "contact": str(self.contact_two.pk),
                    "task": str(self.task.pk),
                    "subject": "Client supplied version",
                    "version": 99,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("version", response.json())

    def test_post_rejects_supplied_status(self):
        response = self.client.post(
            "/api/email-drafts/",
            data=json.dumps(
                {
                    "contact": str(self.contact_two.pk),
                    "task": str(self.task.pk),
                    "subject": "Client supplied status",
                    "status": EmailDraft.Status.SENT.value,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("status", response.json())

    def test_patch_is_not_allowed(self):
        response = self.client.patch(
            f"/api/email-drafts/{self.contact_one_latest.pk}/",
            data=json.dumps({"subject": "Should be ignored"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 405)
        self.contact_one_latest.refresh_from_db()
        self.assertEqual(self.contact_one_latest.subject, "Latest")

    def test_put_is_not_allowed(self):
        response = self.client.put(
            f"/api/email-drafts/{self.contact_one_latest.pk}/",
            data=json.dumps(
                {
                    "contact": str(self.contact_one.pk),
                    "task": str(self.task.pk),
                    "subject": "Should be ignored",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 405)
        self.contact_one_latest.refresh_from_db()
        self.assertEqual(self.contact_one_latest.subject, "Latest")
