import json

from django.test import TestCase

from core.models import EmailDraft
from core.tests.helpers import EmailDraftAPITestMixin


class EmailDraftAPIKnowledgeTests(EmailDraftAPITestMixin, TestCase):
    def test_email_draft_can_create_with_knowledges(self):
        response = self.client.post(
            "/api/email-drafts/",
            data=json.dumps(
                {
                    "contact": str(self.contact_two.pk),
                    "task": str(self.task.pk),
                    "subject": "Created with knowledge",
                    "knowledge_ids": [str(self.knowledge.pk)],
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        draft = EmailDraft.objects.get(pk=response.json()["id"])
        self.assertEqual(
            list(draft.knowledges.values_list("pk", flat=True)),
            [self.knowledge.pk],
        )
        self.assertEqual(response.json()["knowledges"][0]["id"], str(self.knowledge.pk))

    def test_email_drafts_can_filter_by_knowledge(self):
        self.contact_one_latest.knowledges.add(self.knowledge)

        response = self.client.get(
            "/api/email-drafts/",
            {"knowledges": self.knowledge.pk},
        )

        self.assertEqual(self.response_ids(response), {str(self.contact_one_latest.pk)})
