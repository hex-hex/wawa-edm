from rest_framework import viewsets

from .filters import CompanyFilter, ContactFilter
from .models import Company, Contact, EmailDraft, EmailTask, Knowledge, KnowledgeTag
from .serializers import (
    CompanySerializer,
    ContactSerializer,
    EmailDraftSerializer,
    EmailTaskSerializer,
    KnowledgeSerializer,
    KnowledgeTagSerializer,
)


class CompanyViewSet(viewsets.ModelViewSet):
    """CRUD API for companies."""

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filterset_class = CompanyFilter
    search_fields = ["name", "about"]


class ContactViewSet(viewsets.ModelViewSet):
    """CRUD API for contacts."""

    queryset = Contact.objects.select_related("company").all()
    serializer_class = ContactSerializer
    filterset_class = ContactFilter
    search_fields = ["first_name", "middle_name", "last_name", "email", "role", "phone", "behavior", "company__name"]


class KnowledgeTagViewSet(viewsets.ModelViewSet):
    """CRUD API for knowledge tags."""

    queryset = KnowledgeTag.objects.all()
    serializer_class = KnowledgeTagSerializer
    search_fields = ["name"]


class KnowledgeViewSet(viewsets.ModelViewSet):
    """CRUD API for knowledge snippets."""

    queryset = Knowledge.objects.prefetch_related("tags").all()
    serializer_class = KnowledgeSerializer
    filterset_fields = {"tags": ["exact"], "tags__name": ["exact", "icontains"]}
    search_fields = ["abstract", "content"]


class EmailTaskViewSet(viewsets.ModelViewSet):
    """CRUD API for email tasks."""

    queryset = EmailTask.objects.prefetch_related("knowledges").all()
    serializer_class = EmailTaskSerializer
    search_fields = ["name", "target", "strategy"]


class EmailDraftViewSet(viewsets.ModelViewSet):
    """CRUD API for email drafts."""

    queryset = EmailDraft.objects.select_related("contact", "task").all()
    serializer_class = EmailDraftSerializer
    filterset_fields = ["status", "task"]
    search_fields = [
        "title",
        "content",
        "contact__email",
        "contact__first_name",
        "contact__last_name",
    ]
