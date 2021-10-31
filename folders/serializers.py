from rest_framework import serializers
from folders.models import *


class FolderSerializer(serializers.ModelSerializer):
    author_id = serializers.ReadOnlyField()
    author_name = serializers.ReadOnlyField()
    visibility = serializers.BooleanField(default=True)
    class Meta:
        model = Folders
        exclude = ('user','result')
    def create(self, validated_data):
        user = self.context['request'].user
        return Folders.objects.create(**validated_data, user=user)


class FolderDetailSerializer(serializers.ModelSerializer):
    author_id = serializers.ReadOnlyField()
    author_name = serializers.ReadOnlyField()
    result = serializers.ReadOnlyField()
    list_vocabularies = serializers.ReadOnlyField()
    class Meta:
        model = Folders
        exclude = ('user',)