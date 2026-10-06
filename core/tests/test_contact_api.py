import json

from django.test import TestCase

from core.models import Company, Contact, EmailDraft, EmailTask


class ContactAPITests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Wawa")

    def test_create_contact_returns_subscribed_default(self):
        response = self.client.post(
            "/api/contacts/",
            data=json.dumps(
                {
                    "company": str(self.company.pk),
                    "first_name": "Ada",
                    "last_name": "Lovelace",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertIs(response.json()["subscribed"], True)
        self.assertTrue(Contact.objects.get().subscribed)

    def test_filter_contacts_without_email_draft(self):
        with_draft = Contact.objects.create(
            company=self.company,
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
        )
        without_draft = Contact.objects.create(
            company=self.company,
            first_name="Grace",
            last_name="Hopper",
            email="grace@example.com",
        )
        task = EmailTask.objects.create(name="Launch", target="Founders")
        EmailDraft.objects.create(
            contact=with_draft,
            task=task,
            subject="Intro",
            content="Hi Grace, " * 10,
        )

        response = self.client.get(
            "/api/contacts/",
            {"has_email_draft": "false"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {item["id"] for item in response.json()["results"]},
            {str(without_draft.pk)},
        )

    def test_filter_contacts_with_email_draft(self):
        with_draft = Contact.objects.create(
            company=self.company,
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
        )
        Contact.objects.create(
            company=self.company,
            first_name="Grace",
            last_name="Hopper",
            email="grace@example.com",
        )
        task = EmailTask.objects.create(name="Launch", target="Founders")
        EmailDraft.objects.create(
            contact=with_draft,
            task=task,
            subject="Intro",
            content="Hi Grace, " * 10,
        )

        response = self.client.get(
            "/api/contacts/",
            {"has_email_draft": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {item["id"] for item in response.json()["results"]},
            {str(with_draft.pk)},
        )

    def test_filter_has_email_draft_requires_content_length(self):
        task = EmailTask.objects.create(name="Launch", target="Founders")
        empty_content = Contact.objects.create(
            company=self.company,
            first_name="Empty",
            last_name="NoContent",
            email="empty@example.com",
        )
        short_content = Contact.objects.create(
            company=self.company,
            first_name="Short",
            last_name="Body",
            email="short@example.com",
        )
        long_content = Contact.objects.create(
            company=self.company,
            first_name="Long",
            last_name="Body",
            email="long@example.com",
        )
        EmailDraft.objects.create(contact=empty_content, task=task, subject="S")
        EmailDraft.objects.create(
            contact=short_content,
            task=task,
            subject="S",
            content="x" * 49,
        )
        EmailDraft.objects.create(
            contact=long_content,
            task=task,
            subject="S",
            content="x" * 50,
        )

        true_response = self.client.get(
            "/api/contacts/",
            {"has_email_draft": "true"},
        )
        self.assertEqual(true_response.status_code, 200)
        self.assertEqual(
            {item["id"] for item in true_response.json()["results"]},
            {str(long_content.pk)},
        )

        false_response = self.client.get(
            "/api/contacts/",
            {"has_email_draft": "false"},
        )
        self.assertEqual(false_response.status_code, 200)
        self.assertEqual(
            {item["id"] for item in false_response.json()["results"]},
            {str(empty_content.pk), str(short_content.pk)},
        )
