from rest_framework import viewsets

from ..filters import ContactFilter
from ..models import Contact, ContactTag
from ..serializers import ContactSerializer, ContactTagSerializer


class ContactTagViewSet(viewsets.ModelViewSet):
    """CRUD API for contact tags."""

    queryset = ContactTag.objects.all()
    serializer_class = ContactTagSerializer
    search_fields = ["name"]


class ContactViewSet(viewsets.ModelViewSet):
    """CRUD API for contacts."""

    queryset = Contact.objects.select_related("company").prefetch_related("tags").all()
    serializer_class = ContactSerializer
    filterset_class = ContactFilter
    search_fields = [
        "first_name",
        "middle_name",
        "last_name",
        "email",
        "role",
        "phone",
        "behavior",
        "company__name",
    ]
