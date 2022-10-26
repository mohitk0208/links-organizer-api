from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import AccessLevel, Category, CategoryAccess


class CategoryAccessSerializer(serializers.ModelSerializer):
    user_avatar = serializers.ReadOnlyField(source="user.avatar")
    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = CategoryAccess
        fields = (
            "id",
            "user",
            "user_avatar",
            "username",
            "category",
            "level"
        )

        read_only_fields = ("id", "user", "category")


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
