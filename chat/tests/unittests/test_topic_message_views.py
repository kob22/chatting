import datetime
import json
from unittest import mock

import pytz
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory

from chat.models import Topic, Message
from chat.serializers import MessageSerializer
from chat.views import MessageFromTopicViewSet
from chatting.settings import REST_FRAMEWORK


def create_topics_obj():
    topics = [{'id': 1, 'title': 'What is the weather like?'},
              {'id': 2, 'title': 'The Most Popular Color in the World'},
              {'id': 3, 'title': 'The best programming language'},
              {'id': 4, 'title': '10 Best Programming Language to Learn in 2020'}]
    topics_saved = []
    for topic in topics:
        topics_saved.append(Topic.objects.create(**topic))

    return topics_saved


def create_messages_dictionary(topics_objects):
    messages = [{'id': 1, 'text': "Hot and sunny day", 'topic': topics_objects[0]},
                {'id': 2, 'text': "The best color is Blue", 'topic': topics_objects[1]},
                {'id': 3, 'text': "The best language is Python", 'topic': topics_objects[2]},
                {'id': 4, 'text': "Python and JavaScript", 'topic': topics_objects[3]},
                {'id': 5, 'text': "I think it will be cold and snow", 'topic': topics_objects[0]},
                {'id': 6, 'text': "It will be a rainstorm", 'topic': topics_objects[0]},
                {'id': 7, 'text': "The best color is Red", 'topic': topics_objects[1]},
                {'id': 8, 'text': "The best color is Magenta", 'topic': topics_objects[1]}]

    return messages


def create_messages_objects(messages_attr):
    mocked_date = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)

    messages_saved = []
    with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_date)):
        for msg in messages_attr:
            temp_msg = Message.objects.create(**msg)
            messages_saved.append(temp_msg)

    return messages_saved


class MessageFromTopicViewsALLTest(TestCase):

    def setUp(self) -> None:
        self.topics_saved = create_topics_obj()

    def test_view_empty_messages_from_topic(self):
        """Test get all messages when there is no messages for topic"""

        factory = APIRequestFactory()
        message_view = MessageFromTopicViewSet.as_view({'get': 'list'})
        request = factory.get(reverse('message-from-topic-list', args=(self.topics_saved[0].id,)))
        response = message_view(request, topic_id=self.topics_saved[0].id)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), [])
        self.assertEqual(response['content-type'], 'application/json')

    def test_view_all_messages_from_topic(self):
        self.messages = create_messages_dictionary(self.topics_saved)
        self.messages_saved = create_messages_objects(self.messages)

        factory = APIRequestFactory()
        message_view = MessageFromTopicViewSet.as_view({'get': 'list'})
        request = factory.get(reverse('message-from-topic-list', args=(self.topics_saved[1].id,)))
        response = message_view(request, topic_id=self.topics_saved[1].id)
        response.render()

        messages_from_topic = Message.objects.filter(topic_id=self.topics_saved[1].id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), MessageSerializer(messages_from_topic, many=True).data)
        self.assertEqual(response['content-type'], 'application/json')


class MessageFromTopicViewsDetailsTest(TestCase):

    def setUp(self) -> None:
        self.topics_saved = create_topics_obj()

    def test_view_nonexisting_message_from_topic(self):
        factory = APIRequestFactory()
        message_view = MessageFromTopicViewSet.as_view({'get': 'retrieve'})
        request = factory.get(reverse('message-from-topic-detail', args=(self.topics_saved[0].id, 2),))
        response = message_view(request, topic_id=self.topics_saved[0].id, msg_id=2)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {'detail': 'Not found.'})
        self.assertEqual(response['content-type'], 'application/json')

    def test_view_existing_message_from_topic(self):
        self.message = {'id': 1, 'text': "Hot and sunny day", 'topic': self.topics_saved[0]}
        self.message_saved = Message.objects.create(**self.message)

        factory = APIRequestFactory()
        message_view = MessageFromTopicViewSet.as_view({'get': 'retrieve'})
        request = factory.get(reverse('message-from-topic-detail', args=(self.topics_saved[0].id, self.message_saved.id)))
        response = message_view(request, topic_id=self.topics_saved[0].id, msg_id=self.message_saved.id)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), MessageSerializer(self.message_saved).data)
        self.assertEqual(response['content-type'], 'application/json')

    def test_view_existing_message_from_wrong_topic(self):
        self.message = {'id': 1, 'text': "Hot and sunny day", 'topic': self.topics_saved[0]}
        self.message_saved = Message.objects.create(**self.message)

        factory = APIRequestFactory()
        message_view = MessageFromTopicViewSet.as_view({'get': 'retrieve'})
        request = factory.get(reverse('message-from-topic-detail', args=(self.topics_saved[1].id, self.message_saved.id)))
        response = message_view(request, topic_id=self.topics_saved[1].id, msg_id=self.message_saved.id)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {'detail': 'Not found.'})
        self.assertEqual(response['content-type'], 'application/json')


class MessageFromTopicViewsCreateTest(TestCase):

    def setUp(self) -> None:
        self.topics_saved = create_topics_obj()

    def test_view_create_message_with_correct_data_from_topic(self):
        mocked_date = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.message = {'id': 1, 'text': "Hot and sunny day"}

        factory = APIRequestFactory()
        message_view = MessageFromTopicViewSet.as_view(actions={'post': 'create'})
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_date)):
            request = factory.post(reverse('message-from-topic-list', args=(self.topics_saved[0].id,)), self.message)
            response = message_view(request, topic_id=self.topics_saved[0].id)
            response.render()

            self.message['created_at'] = mocked_date.strftime(REST_FRAMEWORK['DATETIME_FORMAT'])

        messages_from_topic = Message.objects.filter(text=self.message['text']).first()


        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), MessageSerializer(messages_from_topic).data)
        self.assertEqual(response['content-type'], 'application/json')

    def test_view_create_message_with_too_short_text_from_topic(self):
        mocked_date = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.message = {'id': 1, 'text': "H" * 9}

        factory = APIRequestFactory()
        message_view = MessageFromTopicViewSet.as_view(actions={'post': 'create'})
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_date)):
            request = factory.post(reverse('message-from-topic-list', args=(self.topics_saved[0].id,)), self.message)
            response = message_view(request, topic_id=self.topics_saved[0].id)
            response.render()

            self.message['created_at'] = mocked_date.strftime(REST_FRAMEWORK['DATETIME_FORMAT'])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content),
                         {'text': ['Ensure this value has at least 10 characters (it has 9).']})
        self.assertEqual(response['content-type'], 'application/json')

    def test_view_create_message_with_additional_attr_from_topic(self):
        mocked_date = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.message = {'id': 1, 'text': "Hot and sunny day", 'additional_attr': 'value'}

        factory = APIRequestFactory()
        message_view = MessageFromTopicViewSet.as_view(actions={'post': 'create'})
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_date)):
            request = factory.post(reverse('message-from-topic-list', args=(self.topics_saved[0].id,)), self.message)
            response = message_view(request, topic_id=self.topics_saved[0].id)
            response.render()

            self.message['created_at'] = mocked_date.strftime(REST_FRAMEWORK['DATETIME_FORMAT'])

        del self.message['additional_attr']

        messages_from_topic = Message.objects.filter(text=self.message['text']).first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), MessageSerializer(messages_from_topic).data)
        self.assertEqual(response['content-type'], 'application/json')

    def test_view_create_message_with_unexisted_topic(self):
        mocked_date = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.message = {'id': 1, 'text': "Hot and sunny day"}

        factory = APIRequestFactory()
        message_view = MessageFromTopicViewSet.as_view(actions={'post': 'create'})
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_date)):
            request = factory.post(reverse('message-from-topic-list', args=(99,)), self.message)
            response = message_view(request, topic_id=99)
            response.render()

            self.message['created_at'] = mocked_date.strftime(REST_FRAMEWORK['DATETIME_FORMAT'])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {'topic': ['Invalid pk "99" - object does not exist.']})
        self.assertEqual(response['content-type'], 'application/json')


class MessageFromTopicViewsUpdateMessage(TestCase):

    def setUp(self) -> None:
        self.topics_saved = create_topics_obj()

        self.messages = create_messages_dictionary(self.topics_saved)
        self.messages_saved = create_messages_objects(self.messages)

    def test_update_message_text_from_topic(self):
        # create messages to update and change Topics object to id
        new_text = 'The worst weather ever'

        msg_after_update = dict(MessageSerializer(instance=self.messages_saved[0]).data)
        msg_after_update['text'] = new_text

        msg_to_send = dict(msg_after_update)
        del msg_to_send['created_at']

        factory = APIRequestFactory()
        message_view = MessageFromTopicViewSet.as_view({'put': 'update'})

        request = factory.put(reverse('message-from-topic-detail', args=(self.messages[0]['topic'].id, self.messages[0]['id'])), msg_to_send)
        response = message_view(request, topic_id=self.messages[0]['topic'].id, msg_id=self.messages[0]['id'])
        response.render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), msg_after_update)
        self.assertEqual(response['content-type'], 'application/json')

    def test_update_message_with_too_short_text_from_topic(self):
        # create messages to update and change Topics object to id
        new_text = 'H' * 9

        msg_after_update = dict(MessageSerializer(instance=self.messages_saved[0]).data)
        msg_after_update['text'] = new_text

        msg_to_send = dict(msg_after_update)
        del msg_to_send['created_at']

        factory = APIRequestFactory()
        message_view = MessageFromTopicViewSet.as_view({'put': 'update'})
        request = factory.put(reverse('message-from-topic-detail', args=(self.messages[0]['topic'].id, self.messages[0]['id'])), msg_to_send)
        response = message_view(request, topic_id=self.messages[0]['topic'].id, msg_id=self.messages[0]['id'])
        response.render()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content),
                         {'text': ['Ensure this value has at least 10 characters (it has 9).']})
        self.assertEqual(response['content-type'], 'application/json')

    def test_update_message_text_with_additionals_attr_from_topic(self):
        # create messages to update and change Topics object to id
        new_text = 'The worst weather ever'

        msg_after_update = dict(MessageSerializer(instance=self.messages_saved[0]).data)
        msg_after_update['text'] = new_text

        msg_to_send = dict(msg_after_update)
        del msg_to_send['created_at']
        msg_to_send['add_attr'] = 'New Value'

        factory = APIRequestFactory()
        message_view = MessageFromTopicViewSet.as_view({'put': 'update'})
        request = factory.put(reverse('message-from-topic-detail', args=(self.messages[0]['topic'].id, self.messages[0]['id'])), msg_to_send)
        response = message_view(request, topic_id=self.messages[0]['topic'].id, msg_id=self.messages[0]['id'])
        response.render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), msg_after_update)
        self.assertEqual(response['content-type'], 'application/json')

    def test_views_update_message_topic_with_diff_topic_in_data_from_topic(self):
        """
        test update message from topic view, URL has correct topic_id but in data is wrong. Message will be updated,
        because topic from request will be overwrite by topic id from URL
        :return:
        """
        msg_after_update = dict(MessageSerializer(instance=self.messages_saved[0]).data)


        msg_to_send = dict(msg_after_update)
        del msg_to_send['created_at']

        factory = APIRequestFactory()
        message_view = MessageFromTopicViewSet.as_view({'put': 'update'})
        request = factory.put(reverse('message-from-topic-detail', args=(self.messages[0]['topic'].id, self.messages[0]['id'])), msg_to_send)
        response = message_view(request, topic_id=self.messages[0]['topic'].id, msg_id=self.messages[0]['id'])
        response.render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), msg_after_update)
        self.assertEqual(response['content-type'], 'application/json')

    def test_views_update_message_topic_with_wrong_topic_id_in_url_from_topic(self):
        """
        """
        msg_after_update = dict(MessageSerializer(instance=self.messages_saved[0]).data)

        msg_to_send = dict(msg_after_update)
        del msg_to_send['created_at']

        factory = APIRequestFactory()
        message_view = MessageFromTopicViewSet.as_view({'put': 'update'})
        request = factory.put(reverse('message-from-topic-detail', args=(22, self.messages[0]['id'])), msg_to_send)
        response = message_view(request, topic_id=22, msg_id=self.messages[0]['id'])
        response.render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {'detail': 'Not found.'} )
        self.assertEqual(response['content-type'], 'application/json')

    def test_views_update_nonexisting_message_from_topic(self):
        """
        """

        factory = APIRequestFactory()
        message_view = MessageFromTopicViewSet.as_view({'put': 'update'})
        request = factory.put(reverse('message-from-topic-detail', args=(1, 22,)), {'text': 'Super Text'})
        response = message_view(request, topic_id=1, msg_id=22)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {'detail': 'Not found.'} )
        self.assertEqual(response['content-type'], 'application/json')


class MessageFromTopicViewsDeleteMessages(TestCase):

    def test_delete_nonexisting_message_from_topic(self):
        factory = APIRequestFactory()
        msg_view = MessageFromTopicViewSet.as_view({'delete': 'destroy'})
        request = factory.delete(reverse('message-from-topic-detail', args=(2,45)))
        response = msg_view(request, topic_id=2, msg_id=45)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {'detail': 'Not found.'})
        self.assertEqual(response['content-type'], 'application/json')

    def test_delete_existing_message(self):
        self.topics_saved = create_topics_obj()
        self.messages = create_messages_dictionary(self.topics_saved)
        self.messages_saved = create_messages_objects(self.messages)

        msg_id = self.messages_saved[1].id
        factory = APIRequestFactory()
        msg_view = MessageFromTopicViewSet.as_view({'delete': 'destroy'})
        request = factory.delete(reverse('message-from-topic-detail', args=(self.messages_saved[1].topic.id,msg_id)))
        response = msg_view(request, topic_id=self.messages_saved[1].topic.id, msg_id=msg_id)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Message.DoesNotExist):
            Message.objects.get(id=msg_id)

