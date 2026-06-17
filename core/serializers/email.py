from rest_framework import serializers

from ..models import EmailDraft, EmailTask, Knowledge
from .knowledge import KnowledgeSerializer


class EmailDraftSerializer(serializers.ModelSerializer):
    contact_name = serializers.SerializerMethodField()
    task_name = serializers.SerializerMethodField()
    knowledges = KnowledgeSerializer(many=True, read_only=True)
    knowledge_ids = serializers.PrimaryKeyRelatedField(
        source="knowledges",
        many=True,
        queryset=Knowledge.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = EmailDraft
        fields = [
            "id",
            "contact",
            "contact_name",
            "task",
            "task_name",
            "knowledges",
            "knowledge_ids",
            "subject",
            "pain_points",
            "content",
            "status",
            "version",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_contact_name(self, obj):
        return str(obj.contact)

    def get_task_name(self, obj):
        return obj.task.name if obj.task_id else None


class EmailTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTask
        fields = [
            "id",
            "name",
            "target",
            "strategy",
            "knowledges",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def to_representation(self, instance):
        # Accept knowledges by id on write, but return full nested objects.
        data = super().to_representation(instance)
        data["knowledges"] = KnowledgeSerializer(
            instance.knowledges.all(),
            many=True,
        ).data
        return data
