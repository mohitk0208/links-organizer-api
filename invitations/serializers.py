from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from categories.models import CategoryAccess

from .models import CategoryInvitation


class BasicCategoryInvitationSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source="sender.username")
    sender_avatar = serializers.ReadOnlyField(source="sender.avatar")

    receiver_username = serializers.ReadOnlyField(source="receiver.username")
    receiver_avatar = serializers.ReadOnlyField(source="receiver.avatar")

    category_name = serializers.ReadOnlyField(source="category.name")
    category_description = serializers.ReadOnlyField(source="category.description")
    category_background_url = serializers.ReadOnlyField(source="category.background_url")

    class Meta:
        model = CategoryInvitation
        fields = (
            "id",
            "category",
            "category_name",
            "category_description",
            "category_background_url",
            "sender",
            "sender_username",
            "sender_avatar",
            "receiver",
            "receiver_username",
            "receiver_avatar",
            "note",
            "access_level",
            "is_accepted",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):

        # sender cannot be the receiver
        if self.context["request"].user.id == attrs["receiver"].id:
            raise ValidationError({"receiver": ("Cannot be same as sender")})

        # invitation already exists
        try:
            invitation = CategoryInvitation.objects.get(sender=self.context["request"].user, receiver=attrs["receiver"], category=attrs["category"])
            raise ValidationError({"detail":("Invitation already sent")})
        except CategoryInvitation.DoesNotExist:
            pass

        # category not owned by sender
        if attrs["category"].owner.id != self.context["request"].user.id:
            raise ValidationError({"detail": ("Category does not exist")})

        # category already shared
        try:
            _ = CategoryAccess.objects.get(user=attrs["receiver"], category=attrs["category"])
            raise ValidationError({"detail": ("category already shared to the user")})
        except CategoryAccess.DoesNotExist :
            pass

        return attrs


class CategoryInvitationSenderSerializer(BasicCategoryInvitationSerializer):
    class Meta(BasicCategoryInvitationSerializer.Meta):
        read_only_fields = ("id", "sender", "created_at", "updated_at", "is_accepted")


class CategoryInvitationReceiverSerializer(BasicCategoryInvitationSerializer):
    class Meta(BasicCategoryInvitationSerializer.Meta):
        read_only_fields = ("id", "sender", "receiver","note","access_level", "created_at", "updated_at")
