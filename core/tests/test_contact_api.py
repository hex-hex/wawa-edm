import json

from django.test import TestCase

from core.models import Company, Contact


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
