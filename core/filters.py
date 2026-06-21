import django_filters
from django.db.models import Exists, OuterRef, Q, Subquery

from .models import Company, Contact, EmailDraft, EmailTask


def latest_drafts_per_contact_for_task(queryset, task):
    task_id = getattr(task, "pk", task)
    if not task_id:
        return queryset

    latest_version = (
        EmailDraft.objects.filter(task_id=task_id, contact_id=OuterRef("contact_id"))
        .order_by("-version")
        .values("version")[:1]
    )
    return queryset.filter(task_id=task_id, version=Subquery(latest_version))


class CompanyFilter(django_filters.FilterSet):
    about_empty = django_filters.BooleanFilter(
        method="filter_about_empty",
        label="about is null or blank",
    )

    class Meta:
        model = Company
        fields = []

    def filter_about_empty(self, queryset, name, value):
        if value is None:
            return queryset
        empty = Q(about__isnull=True) | Q(about__exact="")
        return queryset.filter(empty) if value else queryset.exclude(empty)


class ContactFilter(django_filters.FilterSet):
    story_empty = django_filters.BooleanFilter(
        method="filter_story_empty",
        label="story is null or blank",
    )
    has_email_draft = django_filters.BooleanFilter(
        method="filter_has_email_draft",
        label="has email draft",
    )

    class Meta:
        model = Contact
        fields = ["priority", "gender", "has_email_draft"]

    def filter_story_empty(self, queryset, name, value):
        if value is None:
            return queryset
        empty = Q(story__isnull=True) | Q(story__exact="")
        return queryset.filter(empty) if value else queryset.exclude(empty)

    def filter_has_email_draft(self, queryset, name, value):
        if value is None:
            return queryset

        email_draft_exists = EmailDraft.objects.filter(contact_id=OuterRef("pk"))
        return (
            queryset.filter(Exists(email_draft_exists))
            if value
            else queryset.filter(~Exists(email_draft_exists))
        )


class EmailDraftFilter(django_filters.FilterSet):
    task_latest = django_filters.ModelChoiceFilter(
        queryset=EmailTask.objects.all(),
        method="filter_task_latest",
        label="task latest per contact",
    )

    class Meta:
        model = EmailDraft
        fields = ["status", "task", "knowledges", "task_latest"]

    def filter_task_latest(self, queryset, name, value):
        return latest_drafts_per_contact_for_task(queryset, value)
