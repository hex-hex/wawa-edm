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

    def test_patch_rejects_supplied_version(self):
        response = self.client.patch(
            f"/api/email-drafts/{self.contact_one_latest.pk}/",
            data=json.dumps({"version": 99}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("version", response.json())
        self.contact_one_latest.refresh_from_db()
        self.assertEqual(self.contact_one_latest.version, 2)

    def test_patch_changing_task_generates_next_version_for_new_group(self):
        response = self.client.patch(
            f"/api/email-drafts/{self.contact_one_latest.pk}/",
            data=json.dumps({"task": str(self.other_task.pk)}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["version"], 2)
        self.contact_one_latest.refresh_from_db()
        self.assertEqual(self.contact_one_latest.task, self.other_task)
        self.assertEqual(self.contact_one_latest.version, 2)

    def test_put_rejects_supplied_version(self):
        response = self.client.put(
            f"/api/email-drafts/{self.contact_one_latest.pk}/",
            data=json.dumps(
                {
                    "contact": str(self.contact_one.pk),
                    "task": str(self.task.pk),
                    "subject": "Updated",
                    "status": EmailDraft.Status.DRAFT.value,
                    "version": 99,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("version", response.json())
        self.contact_one_latest.refresh_from_db()
        self.assertEqual(self.contact_one_latest.version, 2)
