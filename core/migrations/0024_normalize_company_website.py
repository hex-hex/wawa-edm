from django.db import migrations


def normalize_empty_websites(apps, schema_editor):
    Company = apps.get_model("core", "Company")
    qs = Company.objects.exclude(website=None)
    updated = []
    for obj in qs:
        if not obj.website.strip():
            obj.website = None
            updated.append(obj)
    if updated:
        Company.objects.bulk_update(updated, ["website"], batch_size=200)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0023_contacttag_contact_tags"),
    ]

    operations = [
        migrations.RunPython(
            normalize_empty_websites,
            reverse_code=noop_reverse,
        ),
    ]
