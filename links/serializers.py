from rest_framework import serializers

from categories.models import Category
from tags.serializers import TagSerializer

from .models import Link


class LinkSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    owner_avatar = serializers.ReadOnlyField(source='owner.avatar')
    category_background_url = serializers.ReadOnlyField(source='category.background_url')
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
          'category_background_url',
          'description',
          'owner',
          'owner_username',
          'owner_avatar',
          'tags',
          'created_at',
          'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'owner')

    def validate(self, attrs):
        try:
            link = Link.objects.get(url=attrs["url"], owner=self.context["request"].user)
            raise serializers.ValidationError({"url": ("This URL is already in use.")})
        except Link.DoesNotExist:
            pass

        try:
            category = Category.objects.get(id=attrs["category"].id, owner=self.context["request"].user)
        except Category.DoesNotExist:
            raise serializers.ValidationError({"category": ["Category does not exist."]})

        return attrs
