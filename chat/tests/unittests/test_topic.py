import datetime
from unittest import mock

import pytz
from django.core.exceptions import ValidationError as ValidationError_DJ
from django.test import TestCase

from rest_framework.exceptions import ValidationError as ValidationError_RF

from chat.models import Topic
from chat.serializers import TopicSerializer
from chatting.settings import REST_FRAMEWORK


class TopicModelTest(TestCase):

    def test_create_topic(self):
        topic = Topic(title='Topic title')
        self.assertEqual(topic.title, 'Topic title')

    def test_topic_has_all_fields(self):
        date_to_mock = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)

        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=date_to_mock)):
            topic = Topic(id=1, title='Topic title')
            topic.save()
            topic.full_clean()

        self.assertEqual(topic.id, 1)

        self.assertTrue(isinstance(topic.title, str))
        self.assertTrue(isinstance(topic.created_at, datetime.datetime))

        self.assertEqual(topic.title, 'Topic title')
        self.assertEqual(topic.created_at.strftime(REST_FRAMEWORK['DATETIME_FORMAT']),
                         date_to_mock.strftime(REST_FRAMEWORK['DATETIME_FORMAT']))

    def test_too_short_title(self):
        topic = Topic(title='W' * 4)
        with self.assertRaises(ValidationError_DJ):
            topic.save()
            topic.full_clean()

    def test_minimum_length_title(self):
        topic = Topic(title='W' * 5)
        topic.save()
        topic.full_clean()  # should not raise ValidationError
        self.assertEqual(topic.title, 'W' * 5)

    def test_too_long_title(self):
        topic = Topic(title='n' * 256)

        with self.assertRaises(ValidationError_DJ):
            topic.save()
            topic.full_clean()

    def test_max_length_title(self):
        topic = Topic(title='n' * 255)
        topic.save()
        topic.full_clean()  # should not raise ValidationError
        self.assertEqual(topic.title, 'n' * 255)

    def test_allow_duplicate_title(self):
        first_topic = Topic(title='Interesting world')
        first_topic.save()
        first_topic.full_clean()

        second_topic = Topic(title='Interesting world')
        second_topic.save()
        second_topic.full_clean()  # should not raise ValidationError
        self.assertEqual(second_topic.title, 'Interesting world')


class TopicSerializerTest(TestCase):

    def setUp(self) -> None:
        mocked = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.topic_attr = {'id': 1, 'title': 'What is the weather like?'}
        self.topic_serialized = {'id': 1, 'title': 'What is the weather like?',
                                 'created_at': mocked.strftime(REST_FRAMEWORK['DATETIME_FORMAT'])}
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            self.topic = Topic.objects.create(**self.topic_attr)
        self.serializer = TopicSerializer(instance=self.topic)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'title', 'created_at'])

    def test_contains_correct_data(self):
        self.assertEqual(self.serializer.data, self.topic_serialized)

    def test_topic_title_too_short(self):
        topic_too_short_attr = {'id': 2, 'title': 'W'*4}
        topic_serialized = TopicSerializer(data=topic_too_short_attr)

        with self.assertRaisesMessage(ValidationError_RF, 'Ensure this field has at least 5 characters.'):
            topic_serialized.is_valid(raise_exception=True)

    def test_topic_title_too_long(self):
        topic_too_long_attr = {'id': 2, 'title': 'W'*256}
        topic_serialized = TopicSerializer(data=topic_too_long_attr)

        with self.assertRaisesMessage(ValidationError_RF, 'Ensure this field has no more than 255 characters.'):
            topic_serialized.is_valid(raise_exception=True)