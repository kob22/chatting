from django.test import TestCase
from django.db.utils import IntegrityError
from chat.models import Topic, Message
from chat.serializers import TopicSerializer
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

        self.assertEqual(msg.text, 'Typical message')
        self.assertEqual(msg.created_at, date_to_mock)