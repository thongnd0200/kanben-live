from rest_framework import serializers
from vocabularies.models import Vocabularies

class SearchingSerializer(serializers.Serializer):
    keyWord = serializers.CharField(max_length=500)