from datetime import datetime, timezone

from django.test import SimpleTestCase

from core.management.commands.fix_data import contact_duplicate_groups


class FixDataContactDuplicateTests(SimpleTestCase):
    def contact_row(self, row_id, email, created_at, updated_at):
        return {
            "id": row_id,
            "first_name": "Ada",
            "middle_name": None,
            "last_name": "Lovelace",
            "email": email,
            "created_at": created_at,
            "updated_at": updated_at,
        }

    def test_contact_email_duplicates_are_case_insensitive(self):
        older = self.contact_row(
            "older",
            "Ada@Example.com",
            datetime(2026, 1, 1, tzinfo=timezone.utc),
            datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        newer = self.contact_row(
            "newer",
            "ada@example.com",
            datetime(2026, 1, 2, tzinfo=timezone.utc),
            datetime(2026, 1, 2, tzinfo=timezone.utc),
        )

        to_delete, groups = contact_duplicate_groups([older, newer])

        self.assertEqual(to_delete, {"older"})
        self.assertEqual(len(groups), 1)
        constraint_name, key_label, keep, losers = groups[0]
        self.assertEqual(constraint_name, "unique_contact_non_empty_email")
        self.assertEqual(key_label, "lower_email='ada@example.com'")
        self.assertEqual(keep["id"], "newer")
        self.assertEqual([row["id"] for row in losers], ["older"])
