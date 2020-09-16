from django.test import TestCase
from django.core.exceptions import ValidationError
from chat.models import Topic
from chat.serializers import TopicSerializer
from unittest import mock
import datetime
import pytz


class TopicModelTest(TestCase):

    def test_create_topic(self):
        topic = Topic(title='Topic title')
        self.assertEqual(topic.title, 'Topic title')

    def test_too_short_title(self):
        topic = Topic(title='W'*4)
        with self.assertRaises(ValidationError):
            topic.save()
            topic.full_clean()

    def test_minimum_length_title(self):
        topic = Topic(title='W'*5)
        topic.save()
        topic.full_clean() # should not raise ValidationError
        self.assertEqual(topic.title, 'W'*5)

    def test_too_long_title(self):
        topic = Topic(title='n'*256)

        with self.assertRaises(ValidationError):
            topic.save()
            topic.full_clean()

    def test_max_length_title(self):
        topic = Topic(title='n'*255)
        topic.save()
        topic.full_clean() # should not raise ValidationError
        self.assertEqual(topic.title, 'n'*255)

    def test_allow_duplicate_title(self):
        first_topic = Topic(title='Interesting world')
        first_topic.save()
        first_topic.full_clean()

        second_topic = Topic(title='Interesting world')
        second_topic.save()
        second_topic.full_clean() # should not raise ValidationError
        self.assertEqual(second_topic.title, 'Interesting world')


class TopicSerializerTest(TestCase):

    def setUp(self) -> None:

        mocked = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.topic_attr = {'id': 1, 'title': 'What is the weather like?'}
        self.topic_serialized = {'id': 1, 'title': 'What is the weather like?', 'created_at': '2020-01-01T00:00:00Z'}
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            self.topic = Topic.objects.create(**self.topic_attr)
        self.serializer = TopicSerializer(instance=self.topic)

    def test_contains_expected_fields(self):

        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'title', 'created_at'])

    def test_contains_correct_data(self):
        self.assertEqual(self.serializer.data, self.topic_serialized)
