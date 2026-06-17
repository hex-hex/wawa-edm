from rest_framework import serializers

from ..models import Knowledge, KnowledgeTag


class KnowledgeTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeTag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class KnowledgeSerializer(serializers.ModelSerializer):
    tag_names = serializers.SlugRelatedField(
        source="tags",
        many=True,
        read_only=True,
        slug_field="name",
    )

    class Meta:
        model = Knowledge
        fields = [
            "id",
            "tags",
            "tag_names",
            "abstract",
            "content",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
