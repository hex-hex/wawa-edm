import json

from django.test import TestCase

from core.models import Company, Contact, EmailDraft, EmailTask, Knowledge


class EmailDraftAPIFilterTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Wawa")
        self.contact_one = Contact.objects.create(
            company=self.company,
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
        )
        self.contact_two = Contact.objects.create(
            company=self.company,
            first_name="Grace",
            last_name="Hopper",
            email="grace@example.com",
        )
        self.task = EmailTask.objects.create(name="Launch", target="Founders")
        self.other_task = EmailTask.objects.create(name="Follow up", target="CTOs")
        self.knowledge = Knowledge.objects.create(
            abstract="Pricing proof",
            content="Use the pricing proof point.",
        )

        self.contact_one_old = EmailDraft.objects.create(
            contact=self.contact_one,
            task=self.task,
            subject="Old",
            version=1,
        )
        self.contact_one_latest = EmailDraft.objects.create(
            contact=self.contact_one,
            task=self.task,
            subject="Latest",
            version=2,
        )
        self.contact_two_latest = EmailDraft.objects.create(
            contact=self.contact_two,
            task=self.task,
            subject="Only",
            version=1,
        )
        self.other_task_draft = EmailDraft.objects.create(
            contact=self.contact_one,
            task=self.other_task,
            subject="Other task",
            version=1,
        )

    def response_ids(self, response):
        self.assertEqual(response.status_code, 200)
        return {item["id"] for item in response.json()["results"]}

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

    def test_email_draft_can_associate_knowledges(self):
        response = self.client.patch(
            f"/api/email-drafts/{self.contact_one_latest.pk}/",
            data=json.dumps({"knowledge_ids": [str(self.knowledge.pk)]}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.contact_one_latest.refresh_from_db()
        self.assertEqual(
            list(self.contact_one_latest.knowledges.values_list("pk", flat=True)),
            [self.knowledge.pk],
        )
        knowledge_data = response.json()["knowledges"][0]
        self.assertEqual(knowledge_data["id"], str(self.knowledge.pk))
        self.assertEqual(knowledge_data["abstract"], "Pricing proof")
        self.assertEqual(knowledge_data["content"], "Use the pricing proof point.")

    def test_email_draft_can_create_with_knowledges(self):
        response = self.client.post(
            "/api/email-drafts/",
            data=json.dumps(
                {
                    "contact": str(self.contact_two.pk),
                    "task": str(self.task.pk),
                    "subject": "Created with knowledge",
                    "version": 2,
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
