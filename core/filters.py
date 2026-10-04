import django_filters
from django.db.models import Exists, OuterRef, Q, Subquery

from .models import Company, Contact, ContactTag, EmailDraft, EmailTask


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
    waiting_for_investigation = django_filters.BooleanFilter(
        method="filter_waiting_for_investigation",
        label=(
            "no contact, or about missing/short/invalid "
            "(<90 meaningful words, or placeholder)"
        ),
    )

    class Meta:
        model = Company
        fields = ["waiting_for_investigation"]

    def filter_waiting_for_investigation(self, queryset, name, value):
        if value is None:
            return queryset
        from .services.company_investigation import evaluate_company

        candidates = (
            queryset.filter(
                Q(contacts__isnull=True)
                | Q(about__isnull=True)
                | Q(about__exact="")
            )
            .distinct()
            .prefetch_related("contacts")
        )
        keep_ids = [
            c.id
            for c in candidates
            if evaluate_company(c).waiting == value
        ]
        return queryset.filter(id__in=keep_ids)


class ContactFilter(django_filters.FilterSet):
    story_empty = django_filters.BooleanFilter(
        method="filter_story_empty",
        label="story is null or blank",
    )
    has_email_draft = django_filters.BooleanFilter(
        method="filter_has_email_draft",
        label="has email draft",
    )
    tags__in = django_filters.ModelMultipleChoiceFilter(
        field_name="tags",
        queryset=ContactTag.objects.all(),
        conjoined=False,
        distinct=True,
        label="tags in (any of the given tag ids)",
    )

    class Meta:
        model = Contact
        fields = ["priority", "has_email_draft", "tags", "tags__in"]

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
