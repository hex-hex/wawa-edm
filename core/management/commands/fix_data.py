"""Clean up data that would violate database constraints.

Currently this removes duplicate ``EmailDraft`` rows that share the same
``(contact, task, version)`` key (the ``unique_emaildraft_contact_task_version``
constraint), keeping the newest row in each group and deleting the rest.

It is safe to run on every startup: it is idempotent, and it no-ops if the
table does not exist yet (e.g. a brand-new database before migrations).

    python manage.py fix_data            # clean up (delete older duplicates)
    python manage.py fix_data --dry-run  # report only, change nothing
"""

from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from core.models import EmailDraft


class Command(BaseCommand):
    help = (
        "Remove duplicate EmailDraft rows (same contact + task + version), "
        "keeping the newest row per group so the unique constraint can apply."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report duplicates without deleting anything.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Run before migrations create the schema: skip cleanly if absent.
        table = EmailDraft._meta.db_table
        if table not in connection.introspection.table_names():
            self.stdout.write(f"Table {table!r} does not exist yet; nothing to clean up.")
            return

        rows = EmailDraft.objects.values(
            "id", "contact_id", "task_id", "version", "created_at", "updated_at"
        )

        groups = defaultdict(list)
        for r in rows:
            groups[(r["contact_id"], r["task_id"], r["version"])].append(r)

        to_delete = []
        dup_groups = 0
        for (contact_id, task_id, version), members in groups.items():
            if len(members) <= 1:
                continue
            dup_groups += 1
            # Newest first: created_at, then updated_at, then id as a stable tie-break.
            members.sort(
                key=lambda r: (r["created_at"], r["updated_at"], str(r["id"])),
                reverse=True,
            )
            keep, *losers = members
            to_delete.extend(r["id"] for r in losers)
            self.stdout.write(
                f"contact={contact_id} task={task_id} version={version}: "
                f"{len(members)} rows -> keep {keep['id']}, delete {len(losers)}"
            )

        self.stdout.write("")
        self.stdout.write(f"Duplicate groups : {dup_groups}")
        self.stdout.write(f"Rows to delete   : {len(to_delete)}")

        if not to_delete:
            self.stdout.write(self.style.SUCCESS("No duplicate EmailDraft rows found."))
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING("Dry run -- nothing deleted. Omit --dry-run to delete.")
            )
            return

        with transaction.atomic():
            deleted, _ = EmailDraft.objects.filter(id__in=to_delete).delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} EmailDraft row(s)."))
