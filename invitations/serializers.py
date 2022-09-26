from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import CategoryInvitation


class BasicCategoryInvitationSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source="sender.username")
    receiver_username = serializers.ReadOnlyField(source="receiver.username")
    sender = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    category_name = serializers.ReadOnlyField(source="category.name")
    category_description = serializers.ReadOnlyField(source="category.description")

    class Meta:
        model = CategoryInvitation
        fields = (
            "id",
            "category",
            "category_name",
            "category_description",
            "sender",
            "sender_username",
            "receiver",
            "receiver_username",
            "is_accepted",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

        validators = [
            UniqueTogetherValidator(
                queryset=CategoryInvitation.objects.all(),
                fields=["sender", "receiver", "category"],
                message="Invitation already exists",
            ),
        ]


class CategoryInvitationListCreateSerializer(BasicCategoryInvitationSerializer):
    class Meta(BasicCategoryInvitationSerializer.Meta):
        read_only_fields = ("id", "is_accepted", "created_at", "updated_at")


class CategoryInvitationDetailSerializer(BasicCategoryInvitationSerializer):
    class Meta(BasicCategoryInvitationSerializer.Meta):
        read_only_fields = (
            "id",
            "category",
            "sender",
            "receiver",
            "created_at",
            "updated_at",
        )
