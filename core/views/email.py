from rest_framework import viewsets

from ..filters import EmailDraftFilter
from ..models import EmailDraft, EmailTask
from ..serializers import EmailDraftSerializer, EmailTaskSerializer


class EmailTaskViewSet(viewsets.ModelViewSet):
    """CRUD API for email tasks."""

    queryset = EmailTask.objects.prefetch_related("knowledges").all()
    serializer_class = EmailTaskSerializer
    search_fields = ["name", "target", "strategy"]


class EmailDraftViewSet(viewsets.ModelViewSet):
    """CRUD API for email drafts."""

    queryset = (
        EmailDraft.objects.select_related("contact", "task")
        .prefetch_related("knowledges")
        .all()
    )
    serializer_class = EmailDraftSerializer
    filterset_class = EmailDraftFilter
    search_fields = [
        "title",
        "content",
        "contact__email",
        "contact__first_name",
        "contact__last_name",
    ]
