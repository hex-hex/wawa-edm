from django.test import TestCase

from core.models import EmailDraft
from core.tests.helpers import EmailDraftAPITestMixin


class EmailDraftAPIFilterTests(EmailDraftAPITestMixin, TestCase):
    def test_task_filter_still_returns_all_drafts_for_task(self):
        response = self.client.get("/api/email-drafts/", {"task": self.task.pk})

        self.assertEqual(
            self.response_ids(response),
            {
                str(self.contact_one_old.pk),
                str(self.contact_one_latest.pk),
                str(self.contact_two_latest.pk),
            },
        )

    def test_task_latest_filter_returns_latest_version_per_contact(self):
        response = self.client.get("/api/email-drafts/", {"task_latest": self.task.pk})

        self.assertEqual(
            self.response_ids(response),
            {
                str(self.contact_one_latest.pk),
                str(self.contact_two_latest.pk),
            },
        )

    def test_task_latest_filter_combines_with_status_after_latest_selection(self):
        response = self.client.get(
            "/api/email-drafts/",
            {"task_latest": self.task.pk, "status": EmailDraft.Status.DRAFT.value},
        )

        self.assertEqual(self.response_ids(response), set())
