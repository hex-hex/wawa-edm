from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

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
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = [
        "first_name",
        "last_name",
        "priority",
        "created_at",
        "updated_at",
    ]
    ordering = ["last_name", "first_name"]
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
