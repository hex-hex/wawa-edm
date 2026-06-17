from rest_framework import viewsets

from ..filters import ContactFilter
from ..models import Contact
from ..serializers import ContactSerializer


class ContactViewSet(viewsets.ModelViewSet):
    """CRUD API for contacts."""

    queryset = Contact.objects.select_related("company").all()
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
