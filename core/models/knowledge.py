import uuid

from django.db import models


class KnowledgeTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=127, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Knowledge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tags = models.ManyToManyField(
        KnowledgeTag,
        related_name="knowledge",
        blank=True,
    )
    abstract = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "knowledge"
        ordering = ["abstract"]

    def __str__(self):
        return self.abstract
