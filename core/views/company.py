from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from ..filters import CompanyFilter
from ..models import Company
from ..serializers import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    """CRUD API for companies."""

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filterset_class = CompanyFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "about"]
    ordering_fields = ["name", "created_at", "updated_at"]
    ordering = ["name"]
