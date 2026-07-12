from rest_framework import serializers

from ..models import Contact, ContactTag


class ContactTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactTag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class ContactSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    tag_names = serializers.SlugRelatedField(
        source="tags",
        many=True,
        read_only=True,
        slug_field="name",
    )

    class Meta:
        model = Contact
        fields = [
            "id",
            "company",
            "company_name",
            "tags",
            "tag_names",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "role",
            "phone",
            "priority",
            "gender",
            "subscribed",
            "behavior",
            "story",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
