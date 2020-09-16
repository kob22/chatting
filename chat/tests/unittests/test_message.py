from django.test import TestCase
from django.db.utils import IntegrityError
from chat.models import Topic, Message
from chat.serializers import MessageSerializer
from chatting.settings import REST_FRAMEWORK
from unittest import mock
import datetime
import pytz


class MessageModelTest(TestCase):

    def setUp(self) -> None:
        self.topic = Topic(title='Best Topic ever')
        self.topic.save()
        self.topic.full_clean() # should not raise ValidationError

    def test_create_message(self):
        msg = Message(text='Typical message', topic=self.topic)
        msg.save()
        msg.full_clean()

    def test_create_message_without_topic(self):
        msg = Message(text='Typical message')
        with self.assertRaises(IntegrityError):
            msg.save()
            msg.full_clean()

    def test_message_has_all_fields(self):
        date_to_mock = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)

        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=date_to_mock)):
            msg = Message(id=1, text='Typical message', topic=self.topic)
            msg.save()
            msg.full_clean()

        self.assertEqual(msg.id, 1)

        self.assertTrue(isinstance(msg.text, str))
        self.assertTrue(isinstance(msg.created_at, datetime.datetime))
        self.assertTrue(isinstance(msg.topic, Topic))

        self.assertEqual(msg.text, 'Typical message')
        self.assertEqual(msg.created_at, date_to_mock)
        self.assertEqual(msg.topic, self.topic)


class MessageSerializerTest(TestCase):

    def setUp(self) -> None:

        date_to_mock = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.topic_attr = {'id': 1, 'title': 'What is the weather like?'}
        self.topic = Topic.objects.create(**self.topic_attr)

        self.message_attr = {'id': 1, 'text': 'Its sunny day', 'topic': self.topic}
        self.message_serialized = {'id': 1, 'text': 'Its sunny day', 'topic': self.topic.id, 'created_at': date_to_mock.strftime(REST_FRAMEWORK['DATETIME_FORMAT'])}
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=date_to_mock)):
            self.message = Message.objects.create(**self.message_attr)

        self.serializer = MessageSerializer(instance=self.message)

    def test_contains_expected_fields(self):

        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'text', 'topic', 'created_at'])

    def test_contains_correct_data(self):
        self.assertEqual(self.serializer.data, self.message_serialized)