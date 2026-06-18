from django.db import IntegrityError, transaction
from django.test import TestCase

from core.models import Company, Contact


class ContactConstraintTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Wawa")

    def test_name_parts_and_email_are_unique_together(self):
        Contact.objects.create(
            company=self.company,
            first_name="Ada",
            middle_name=None,
            last_name="Lovelace",
            email=None,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            Contact.objects.create(
                company=self.company,
                first_name="Ada",
                middle_name=None,
                last_name="Lovelace",
                email=None,
            )

    def test_non_empty_email_is_unique(self):
        Contact.objects.create(
            company=self.company,
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            Contact.objects.create(
                company=self.company,
                first_name="Grace",
                last_name="Hopper",
                email="ada@example.com",
            )

    def test_empty_email_can_be_reused_for_different_name_combinations(self):
        Contact.objects.create(
            company=self.company,
            first_name="Ada",
            last_name="Lovelace",
            email="",
        )
        Contact.objects.create(
            company=self.company,
            first_name="Grace",
            last_name="Hopper",
            email="",
        )
