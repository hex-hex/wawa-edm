from rest_framework import viewsets

from .models import Company, Contact, EmailDraft, EmailTask, Knowledge
from .serializers import (
    CompanySerializer,
    ContactSerializer,
    EmailDraftSerializer,
    EmailTaskSerializer,
    KnowledgeSerializer,
)


class CompanyViewSet(viewsets.ModelViewSet):
    """CRUD API for companies."""

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    search_fields = ["name", "about"]


class ContactViewSet(viewsets.ModelViewSet):
    """CRUD API for contacts."""

    queryset = Contact.objects.select_related("company").all()
    serializer_class = ContactSerializer
    search_fields = ["first_name", "last_name", "email", "role", "phone", "company__name"]


class KnowledgeViewSet(viewsets.ModelViewSet):
    """CRUD API for knowledge snippets."""

    queryset = Knowledge.objects.all()
    serializer_class = KnowledgeSerializer
    search_fields = ["abstract", "content"]


class EmailTaskViewSet(viewsets.ModelViewSet):
    """CRUD API for email tasks."""

    queryset = EmailTask.objects.prefetch_related("knowledges").all()
    serializer_class = EmailTaskSerializer
    search_fields = ["name", "target", "strategy"]


class EmailDraftViewSet(viewsets.ModelViewSet):
    """CRUD API for email drafts."""

    queryset = EmailDraft.objects.select_related("contact").all()
    serializer_class = EmailDraftSerializer
    filterset_fields = ["status"]
    search_fields = [
        "title",
        "content",
        "contact__email",
        "contact__first_name",
        "contact__last_name",
    ]
