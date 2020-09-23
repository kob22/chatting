from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import Topic, Message


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('id', 'title', 'created_at')


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message

        fields = ('id', 'text', 'topic', 'created_at')

    def validate_topic(self, data):
        instance = self.instance

        if instance is not None:
            prievous_topic_id = instance.topic.id
            new_topic_id = data.id
            if new_topic_id is not None and (prievous_topic_id != new_topic_id):
                raise ValidationError('Cannot update message topic')
        return data
