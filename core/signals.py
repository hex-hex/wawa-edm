from django.db.models import Max
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import EmailDraft


@receiver(post_save, sender=EmailDraft)
def sync_email_draft_statuses(sender, instance, **kwargs):
    """Keep one EmailDraft 'scheduled' per (contact, task) group.

    Within a (contact, task) combination, the highest-version draft becomes
    ``scheduled`` and every lower-version draft becomes ``draft``.

    All writes go through queryset ``.update()``, which does **not** emit
    ``post_save`` — so this handler never re-triggers itself.
    """
    # Skip fixture loading and drafts that aren't tied to a task.
    if kwargs.get("raw") or instance.task_id is None:
        return

    group = EmailDraft.objects.filter(
        contact_id=instance.contact_id,
        task_id=instance.task_id,
    )
    max_version = group.aggregate(m=Max("version"))["m"]
    if max_version is None:
        return

    # Highest version -> scheduled; everything below -> draft. exclude() keeps
    # us from writing rows that already hold the target status.
    group.filter(version=max_version).exclude(
        status=EmailDraft.Status.SCHEDULED
    ).update(status=EmailDraft.Status.SCHEDULED)
    group.filter(version__lt=max_version).exclude(
        status=EmailDraft.Status.DRAFT
    ).update(status=EmailDraft.Status.DRAFT)

    # Reflect the new status on the in-memory instance so the API/admin response
    # matches the database without an extra save().
    new_status = (
        EmailDraft.Status.SCHEDULED
        if instance.version == max_version
        else EmailDraft.Status.DRAFT
    )
    if instance.status != new_status:
        instance.status = new_status
