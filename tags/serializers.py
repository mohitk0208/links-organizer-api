from rest_framework import serializers

from .models import Tag


class TagDetailSerializer(serializers.ModelSerializer):
    """Tag Detail Serializer"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'description', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class TagSerializer(serializers.ModelSerializer):
    """Tag Serializer"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
