from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    owner_avatar = serializers.ReadOnlyField(source='owner.avatar')

    class Meta:
        model = Category
        fields = (
          'id',
          'name',
          'owner',
          'owner_username',
          'owner_avatar',
          'created_at',
          'updated_at',
          'parent_category'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'owner')
