from rest_framework import serializers

from .models import Company, Contact, EmailDraft, EmailTask, Knowledge


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "about", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ContactSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = Contact
        fields = [
            "id",
            "company",
            "company_name",
            "first_name",
            "last_name",
            "email",
            "role",
            "phone",
            "story",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class KnowledgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Knowledge
        fields = ["id", "abstract", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class EmailDraftSerializer(serializers.ModelSerializer):
    contact_name = serializers.SerializerMethodField()

    class Meta:
        model = EmailDraft
        fields = [
            "id",
            "contact",
            "contact_name",
            "title",
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
