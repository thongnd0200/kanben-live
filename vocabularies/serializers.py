from rest_framework import serializers
from vocabularies.models import Vocabularies

class VocabularySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vocabularies
        fields = '__all__'