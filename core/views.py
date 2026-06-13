from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from .models import Company, Contact
from .serializers import CompanySerializer, ContactSerializer


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
