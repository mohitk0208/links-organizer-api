from rest_framework import serializers

from .models import Link
from tags.serializers import TagSerializer


class LinkSerializer(serializers.ModelSerializer):
    owner__username = serializers.ReadOnlyField(source='owner.username')
    owner__avatar = serializers.ReadOnlyField(source='owner.avatar')
    # tags = TagSerializer(many=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['tags'] = TagSerializer(instance.tags.all(), many=True).data
        return ret

    class Meta:
        model = Link
        fields = (
          'id',
          'url',
          'category',
          'description',
          'owner',
          'owner__username',
          'owner__avatar',
          'tags',
          'created_at',
          'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'owner')
