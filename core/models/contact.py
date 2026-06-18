import uuid

from django.db import models

from .company import Company


class Contact(models.Model):
    class Priority(models.TextChoices):
        HOT = "hot", "Hot"
        WARM = "warm", "Warm"
        COLD = "cold", "Cold"

    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="contacts",
    )
    first_name = models.CharField(max_length=150, blank=True, null=True)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    role = models.CharField(max_length=63, blank=True, null=True)
    phone = models.CharField(max_length=63, blank=True, null=True)
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        blank=True,
        null=True,
    )
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
        null=True,
    )
    behavior = models.TextField(blank=True, null=True)
    story = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "middle_name", "last_name", "email"],
                name="unique_contact_name_email",
                nulls_distinct=False,
            ),
            models.UniqueConstraint(
                fields=["email"],
                condition=models.Q(email__isnull=False) & ~models.Q(email=""),
                name="unique_contact_non_empty_email",
            ),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
