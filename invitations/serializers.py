from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import CategoryInvitation


class BasicCategoryInvitationSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source="sender.username")
    receiver_username = serializers.ReadOnlyField(source="receiver.username")

    class Meta:
        model = CategoryInvitation
        fields = (
            "id",
            "category",
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

    def validate(self, attrs):
        """
        Check if the category is owned by the sender.
        """
        if attrs["category"].owner != attrs["sender"]:
            raise serializers.ValidationError(
                "You can't invite someone else to a category you don't own."
            )

        return attrs


class CategoryInvitationListCreateSerializer(BasicCategoryInvitationSerializer):
    class Meta(BasicCategoryInvitationSerializer.Meta):
        read_only_fields = ("id", "sender", "is_accepted", "created_at", "updated_at")


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
