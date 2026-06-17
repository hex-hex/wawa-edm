from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Knowledge, KnowledgeTag
from ..serializers import KnowledgeSerializer, KnowledgeTagSerializer


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

    @action(detail=False, methods=["get"], url_path="abstract")
    def abstract(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        data = queryset.values("id", "abstract")
        return Response(list(data))
