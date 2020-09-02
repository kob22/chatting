from .models import Topic
from rest_framework import serializers


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('id', 'title', 'created_at')