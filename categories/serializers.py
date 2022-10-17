from rest_framework import serializers

from .models import AccessLevel, Category, CategoryAccess


class CategoryAccessSerializer(serializers.ModelSerializer):
    user_avatar = serializers.ReadOnlyField(source="user.avatar")
    username = serializers.ReadOnlyField(source="user.username")
    user_id = serializers.ReadOnlyField(source="user.id")

    class Meta:
        model = CategoryAccess
        fields = ("id", "user_id", "user_avatar", "username", "level")
        extra_kwargs = {"level": {"required": True}}


class CategorySerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source="owner.username")
    owner_avatar = serializers.ReadOnlyField(source="owner.avatar")
    shared_users = CategoryAccessSerializer(
        source="categoryaccess_set", read_only=True, many=True
    )

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "description",
            "background_url",
            "owner",
            "owner_username",
            "owner_avatar",
            "shared_users",
            "created_at",
            "updated_at",
            "parent_category",
        )
        read_only_fields = ("id", "created_at", "updated_at", "owner")
