from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from .models import Company, Contact, EmailTask, Knowledge
from .serializers import (
    CompanySerializer,
    ContactSerializer,
    EmailTaskSerializer,
    KnowledgeSerializer,
)


class CompanyViewSet(viewsets.ModelViewSet):
    """CRUD API for companies."""

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "about"]


class ContactViewSet(viewsets.ModelViewSet):
    """CRUD API for contacts."""

    queryset = Contact.objects.select_related("company").all()
    serializer_class = ContactSerializer
    filter_backends = [SearchFilter]
    search_fields = ["first_name", "last_name", "email", "company__name"]


class KnowledgeViewSet(viewsets.ModelViewSet):
    """CRUD API for knowledge snippets."""

    queryset = Knowledge.objects.all()
    serializer_class = KnowledgeSerializer
    filter_backends = [SearchFilter]
    search_fields = ["abstract", "content"]


class EmailTaskViewSet(viewsets.ModelViewSet):
    """CRUD API for email tasks."""

    queryset = EmailTask.objects.prefetch_related("knowledges").all()
    serializer_class = EmailTaskSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "target", "strategy"]
