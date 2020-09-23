import datetime
from unittest import mock

import pytz
from django.db.utils import IntegrityError
from django.test import TestCase

from chat.models import Topic, Message
from chat.serializers import MessageSerializer
from chatting.settings import REST_FRAMEWORK


class MessageModelTest(TestCase):

    def setUp(self) -> None:
        self.topic = Topic(title='Best Topic ever')
        self.topic.save()
        self.topic.full_clean()  # should not raise ValidationError

    def test_create_message(self):
        msg = Message(text='Typical message', topic=self.topic)
        msg.save()
        msg.full_clean()

    def test_create_message_without_topic(self):
        msg = Message(text='Typical message')
        with self.assertRaises(IntegrityError):
            msg.save()
            msg.full_clean()

    def test_create_message_with_nontopic_instance(self):
        with self.assertRaises(ValueError):
            msg = Message(text='Typical message', topic=2)
            msg.save()
            msg.full_clean()

    def test_create_message_with_nonsaved_topic_instance(self):
        self.topic = Topic()

        with self.assertRaises(ValueError):
            msg = Message(text='Typical message', topic=self.topic)
            msg.save()
            msg.full_clean()

    def test_update_message_cannot_change_topic(self):
        msg = Message(text='Typical message', topic=self.topic)
        msg.save()
        msg.full_clean()

        self.another_topic = Topic(title='Best Topic ever')
        self.another_topic.save()
        self.another_topic.full_clean()

        with self.assertRaisesMessage(ValueError, 'You cannot change the topic of the message'):
            msg.topic = self.another_topic
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

    def test_delete_topics_removes_all_messages(self):
        for id in range(1, 5):
            msg = Message(id=id, text=f'Typical message number{id}', topic=self.topic)
            msg.save()
            msg.full_clean()

        self.assertEquals(4, len(Message.objects.filter(topic=self.topic)))

        self.topic.delete()

        self.assertEquals(0, len(Message.objects.filter(topic=self.topic)))


class MessageSerializerTest(TestCase):

    def setUp(self) -> None:
        date_to_mock = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.topic_attr = {'id': 1, 'title': 'What is the weather like?'}
        self.topic = Topic.objects.create(**self.topic_attr)

        self.message_attr = {'id': 1, 'text': 'Its sunny day', 'topic': self.topic}
        self.message_serialized = {'id': 1, 'text': 'Its sunny day', 'topic': self.topic.id,
                                   'created_at': date_to_mock.strftime(REST_FRAMEWORK['DATETIME_FORMAT'])}
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=date_to_mock)):
            self.message = Message.objects.create(**self.message_attr)

        self.serializer = MessageSerializer(instance=self.message)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'text', 'topic', 'created_at'])

    def test_contains_correct_data(self):
        self.assertEqual(self.serializer.data, self.message_serialized)

    def test_cant_update_message_topic(self):
        new_topic_attr = {'id': 2, 'title': 'Best color'}
        new_topic = Topic.objects.create(**new_topic_attr)

        serializer = MessageSerializer(self.message, data={'topic': new_topic.id}, partial=True)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors, {'topic': ['Cannot update message topic']})

    def test_update_message(self):
        serializer = MessageSerializer(self.message, data={'text': 'Updated message'}, partial=True)

        self.assertTrue(serializer.is_valid())
        serializer.save()

        msg = Message.objects.get(id=serializer.data['id'])
        self.assertEqual(msg.text, 'Updated message')
