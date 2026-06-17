from core.models import Company, Contact, EmailDraft, EmailTask, Knowledge


class EmailDraftAPITestMixin:
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
