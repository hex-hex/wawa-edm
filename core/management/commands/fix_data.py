"""Clean up data that would violate database uniqueness constraints.

This removes duplicate ``Contact`` rows that would violate the contact unique
constraints, and duplicate ``EmailDraft`` rows that share the same
``(contact, task, version)`` key. For each duplicate group it keeps the newest
row and deletes the rest.

It is safe to run on every startup: it is idempotent, and it no-ops if the
table does not exist yet (e.g. a brand-new database before migrations).

    python manage.py fix_data            # clean up (delete older duplicates)
    python manage.py fix_data --dry-run  # report only, change nothing
"""

from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from core.models import Contact, EmailDraft


CONTACT_REQUIRED_COLUMNS = {
    "id",
    "first_name",
    "middle_name",
    "last_name",
    "email",
    "created_at",
    "updated_at",
}
EMAIL_DRAFT_REQUIRED_COLUMNS = {
    "id",
    "contact_id",
    "task_id",
    "version",
    "created_at",
    "updated_at",
}


def newest_row_key(row):
    return (row["updated_at"], row["created_at"], str(row["id"]))


def duplicate_groups(rows, key_func):
    groups = defaultdict(list)
    for row in rows:
        groups[key_func(row)].append(row)

    for key, members in groups.items():
        if len(members) <= 1:
            continue
        members.sort(key=newest_row_key, reverse=True)
        keep, *losers = members
        yield key, keep, losers


class Command(BaseCommand):
    help = (
        "Remove rows that would violate unique constraints, keeping the newest "
        "row per duplicate group so migrations can apply."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report duplicates without deleting anything.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        existing_tables = set(connection.introspection.table_names())

        total_to_delete = 0
        total_deleted = 0

        contact_to_delete, contact_deleted = self.clean_contact_duplicates(
            dry_run=dry_run,
            existing_tables=existing_tables,
        )
        total_to_delete += contact_to_delete
        total_deleted += contact_deleted

        draft_to_delete, draft_deleted = self.clean_email_draft_duplicates(
            dry_run=dry_run,
            existing_tables=existing_tables,
        )
        total_to_delete += draft_to_delete
        total_deleted += draft_deleted

        if total_to_delete == 0:
            self.stdout.write(self.style.SUCCESS("No duplicate rows found."))
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING("Dry run -- nothing deleted. Omit --dry-run to delete.")
            )
            return

        self.stdout.write(self.style.SUCCESS(f"Deleted {total_deleted} database row(s)."))

    def clean_contact_duplicates(self, *, dry_run, existing_tables):
        # Run before migrations create the schema: skip cleanly if absent.
        table = Contact._meta.db_table
        if table not in existing_tables:
            self.stdout.write(f"Table {table!r} does not exist yet; skipping Contact.")
            return 0, 0
        if not self.table_has_columns(table, CONTACT_REQUIRED_COLUMNS):
            return 0, 0

        rows = list(
            Contact.objects.values(
                "id",
                "first_name",
                "middle_name",
                "last_name",
                "email",
                "created_at",
                "updated_at",
            )
        )

        to_delete = set()
        duplicate_group_count = 0

        non_empty_email_rows = [
            row for row in rows if row["email"] is not None and row["email"] != ""
        ]
        for email, keep, losers in duplicate_groups(
            non_empty_email_rows,
            key_func=lambda row: row["email"],
        ):
            duplicate_group_count += 1
            to_delete.update(row["id"] for row in losers)
            self.stdout.write(
                "Contact unique_contact_non_empty_email "
                f"email={email!r}: {len(losers) + 1} rows -> "
                f"keep {keep['id']}, delete {len(losers)}"
            )

        remaining_rows = [row for row in rows if row["id"] not in to_delete]
        for name_email, keep, losers in duplicate_groups(
            remaining_rows,
            key_func=lambda row: (
                row["first_name"],
                row["middle_name"],
                row["last_name"],
                row["email"],
            ),
        ):
            duplicate_group_count += 1
            to_delete.update(row["id"] for row in losers)
            self.stdout.write(
                "Contact unique_contact_name_email "
                f"key={name_email!r}: {len(losers) + 1} rows -> "
                f"keep {keep['id']}, delete {len(losers)}"
            )

        self.stdout.write("")
        self.stdout.write(f"Contact duplicate groups : {duplicate_group_count}")
        self.stdout.write(f"Contact rows to delete   : {len(to_delete)}")

        if not to_delete or dry_run:
            return len(to_delete), 0

        with transaction.atomic():
            deleted, _ = Contact.objects.filter(id__in=to_delete).delete()
        return len(to_delete), deleted

    def clean_email_draft_duplicates(self, *, dry_run, existing_tables):
        # Run before migrations create the schema: skip cleanly if absent.
        table = EmailDraft._meta.db_table
        if table not in existing_tables:
            self.stdout.write(f"Table {table!r} does not exist yet; skipping EmailDraft.")
            return 0, 0
        if not self.table_has_columns(table, EMAIL_DRAFT_REQUIRED_COLUMNS):
            return 0, 0

        rows = EmailDraft.objects.values(
            "id", "contact_id", "task_id", "version", "created_at", "updated_at"
        )

        to_delete = []
        duplicate_group_count = 0
        for (contact_id, task_id, version), keep, losers in duplicate_groups(
            rows,
            key_func=lambda row: (row["contact_id"], row["task_id"], row["version"]),
        ):
            duplicate_group_count += 1
            to_delete.extend(r["id"] for r in losers)
            self.stdout.write(
                "EmailDraft unique_emaildraft_contact_task_version "
                f"contact={contact_id} task={task_id} version={version}: "
                f"{len(losers) + 1} rows -> keep {keep['id']}, delete {len(losers)}"
            )

        self.stdout.write("")
        self.stdout.write(f"EmailDraft duplicate groups : {duplicate_group_count}")
        self.stdout.write(f"EmailDraft rows to delete   : {len(to_delete)}")

        if not to_delete or dry_run:
            return len(to_delete), 0

        with transaction.atomic():
            deleted, _ = EmailDraft.objects.filter(id__in=to_delete).delete()
        return len(to_delete), deleted

    def table_has_columns(self, table, required_columns):
        with connection.cursor() as cursor:
            actual_columns = {
                column.name
                for column in connection.introspection.get_table_description(
                    cursor, table
                )
            }
        missing_columns = sorted(required_columns - actual_columns)
        if missing_columns:
            self.stdout.write(
                f"Table {table!r} is missing columns {missing_columns}; skipping."
            )
            return False
        return True
