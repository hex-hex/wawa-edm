import uuid

from django.db import models

from .contact import Contact
from .knowledge import Knowledge


class EmailTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    target = models.CharField(max_length=255)
    strategy = models.TextField(blank=True)
    knowledges = models.ManyToManyField(
        Knowledge,
        related_name="email_tasks",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class EmailDraft(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SCHEDULED = "scheduled", "Scheduled"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name="email_drafts",
    )
    task = models.ForeignKey(
        EmailTask,
        on_delete=models.SET_NULL,
        related_name="email_drafts",
        null=True,
        blank=True,
        help_text="The EmailTask this draft was written under the guidance of.",
    )
    knowledges = models.ManyToManyField(
        Knowledge,
        related_name="email_drafts",
        blank=True,
    )
    subject = models.CharField(max_length=255, blank=True, null=True)
    pain_points = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    version = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["contact", "task", "version"],
                name="unique_emaildraft_contact_task_version",
            )
        ]

    def __str__(self):
        return self.subject or f"Draft {self.pk}"
