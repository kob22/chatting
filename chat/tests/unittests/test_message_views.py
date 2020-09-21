from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from chatting.settings import REST_FRAMEWORK
from chat.serializers import MessageSerializer
from rest_framework import status
from chat.models import Topic, Message
from chat.views import MessageViewSet
from unittest import mock
import json
import datetime
import pytz


class MessageViewsALLTest(TestCase):

    def setUp(self) -> None:
        self.topics = [{'id': 1, 'title': 'What is the weather like?'}, {'id': 2, 'title': 'The Most Popular Color in the World'},
                       {'id': 3, 'title': 'The best programming language'}, {'id': 4, 'title': '10 Best Programming Language to Learn in 2020'}]
        self.topics_saved = []
        for topic in self.topics:
            self.topics_saved.append(Topic.objects.create(**topic))

    def test_view_empty_list_all_messages(self):
        """Test get all messages when there is no messages"""
        factory = APIRequestFactory()
        message_view = MessageViewSet.as_view({'get': 'list'})
        request = factory.get(reverse('messages-list'))
        response = message_view(request)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), [])
        self.assertEqual(response['content-type'], 'application/json')

    def test_view_all_messages(self):
        mocked_date = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.messages = [{'id': 1, 'text': "Hot and sunny day", 'topic': self.topics_saved[0]}, {'id': 2, 'text': "Blue", 'topic': self.topics_saved[1]},
                         {'id': 3, 'text': "Python", 'topic': self.topics_saved[2]}, {'id': 4, 'text': "Python and JavaScript", 'topic': self.topics_saved[3]},
                         {'id': 5, 'text': "Cold and snow", 'topic': self.topics_saved[0]}, {'id': 6, 'text': "Rainstorm", 'topic': self.topics_saved[0]}]

        self.messages_saved = []
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_date)):
            for msg in self.messages:
                temp_msg = Message.objects.create(**msg)
                self.messages_saved.append(temp_msg)

        factory = APIRequestFactory()
        message_view = MessageViewSet.as_view({'get': 'list'})
        request = factory.get(reverse('messages-list'))
        response = message_view(request)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), MessageSerializer(self.messages_saved, many=True).data)
        self.assertEqual(response['content-type'], 'application/json')


class MessageViewsDetailsTest(TestCase):

    def setUp(self) -> None:
        self.topics = [{'id': 1, 'title': 'What is the weather like?'}, {'id': 2, 'title': 'The Most Popular Color in the World'},
                       {'id': 3, 'title': 'The best programming language'}, {'id': 4, 'title': '10 Best Programming Language to Learn in 2020'}]
        self.topics_saved = []
        for topic in self.topics:
            self.topics_saved.append(Topic.objects.create(**topic))

    def test_view_nonexisting_message(self):
        factory = APIRequestFactory()
        message_view = MessageViewSet.as_view({'get': 'retrieve'})
        request = factory.get(reverse('messages-detail', args=(1,)))
        response = message_view(request, pk=1)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {'detail': 'Not found.'})
        self.assertEqual(response['content-type'], 'application/json')

    def test_view_existing_message(self):

        self.message = {'id': 1, 'text': "Hot and sunny day", 'topic': self.topics_saved[0]}
        self.message_saved = Message.objects.create(**self.message)

        factory = APIRequestFactory()
        message_view = MessageViewSet.as_view({'get': 'retrieve'})
        request = factory.get(reverse('messages-detail', args=(1,)))
        response = message_view(request, pk=1)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), MessageSerializer(self.message_saved).data)
        self.assertEqual(response['content-type'], 'application/json')


class MessageViewsCreateTest(TestCase):

    def setUp(self) -> None:
        self.topics = [{'id': 1, 'title': 'What is the weather like?'}, {'id': 2, 'title': 'The Most Popular Color in the World'},
                       {'id': 3, 'title': 'The best programming language'}, {'id': 4, 'title': '10 Best Programming Language to Learn in 2020'}]
        self.topics_saved = []
        for topic in self.topics:
            self.topics_saved.append(Topic.objects.create(**topic))

    def test_view_create_message_with_correct_data(self):

        mocked_date = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.message = {'id': 1, 'text': "Hot and sunny day", 'topic': 1}

        factory = APIRequestFactory()
        message_view = MessageViewSet.as_view(actions={'post': 'create'})
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_date)):
            request = factory.post(reverse('messages-list'), self.message)
            response = message_view(request)
            response.render()

            self.message['created_at'] = mocked_date.strftime(REST_FRAMEWORK['DATETIME_FORMAT'])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), self.message)
        self.assertEqual(response['content-type'], 'application/json')

    def test_view_create_message_with_too_short_text(self):

        mocked_date = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.message = {'id': 1, 'text': "H"*9, 'topic': 1}

        factory = APIRequestFactory()
        message_view = MessageViewSet.as_view(actions={'post': 'create'})
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_date)):
            request = factory.post(reverse('messages-list'), self.message)
            response = message_view(request)
            response.render()

            self.message['created_at'] = mocked_date.strftime(REST_FRAMEWORK['DATETIME_FORMAT'])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {'text': ['Ensure this value has at least 10 characters (it has 9).']})
        self.assertEqual(response['content-type'], 'application/json')

    def test_view_create_message_with_additiona_attr(self):

        mocked_date = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.message = {'id': 1, 'text': "Hot and sunny day", 'topic': 1, 'additional_attr': 'value'}

        factory = APIRequestFactory()
        message_view = MessageViewSet.as_view(actions={'post': 'create'})
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_date)):
            request = factory.post(reverse('messages-list'), self.message)
            response = message_view(request)
            response.render()

            self.message['created_at'] = mocked_date.strftime(REST_FRAMEWORK['DATETIME_FORMAT'])

        del self.message['additional_attr']

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), self.message)
        self.assertEqual(response['content-type'], 'application/json')

    def test_view_create_message_without_topic_id(self):

        mocked_date = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.message = {'id': 1, 'text': "Hot and sunny day"}

        factory = APIRequestFactory()
        message_view = MessageViewSet.as_view(actions={'post': 'create'})
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_date)):
            request = factory.post(reverse('messages-list'), self.message)
            response = message_view(request)
            response.render()

            self.message['created_at'] = mocked_date.strftime(REST_FRAMEWORK['DATETIME_FORMAT'])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {'topic': ['This field is required.']})
        self.assertEqual(response['content-type'], 'application/json')

    def test_view_create_message_with_incorrect_topic_id(self):

        mocked_date = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.message = {'id': 1, 'text': "Hot and sunny day", 'topic': 22}

        factory = APIRequestFactory()
        message_view = MessageViewSet.as_view(actions={'post': 'create'})
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_date)):
            request = factory.post(reverse('messages-list'), self.message)
            response = message_view(request)
            response.render()

            self.message['created_at'] = mocked_date.strftime(REST_FRAMEWORK['DATETIME_FORMAT'])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {'topic': [f"Invalid pk \"{self.message['topic']}\" - object does not exist."]})
        self.assertEqual(response['content-type'], 'application/json')


class MessagesViewsUpdateMessage(TestCase):

    def setUp(self) -> None:
        self.topics = [{'id': 1, 'title': 'What is the weather like?'}, {'id': 2, 'title': 'The Most Popular Color in the World'},
                       {'id': 3, 'title': 'The best programming language'}, {'id': 4, 'title': '10 Best Programming Language to Learn in 2020'}]
        self.topics_saved = []
        for topic in self.topics:
            self.topics_saved.append(Topic.objects.create(**topic))

        self.messages = [{'id': 1, 'text': "Hot and sunny day", 'topic': self.topics_saved[0]},
                         {'id': 2, 'text': "Blue", 'topic': self.topics_saved[1]},
                         {'id': 3, 'text': "Python", 'topic': self.topics_saved[2]},
                         {'id': 4, 'text': "Python and JavaScript", 'topic': self.topics_saved[3]},
                         {'id': 5, 'text': "Cold and snow", 'topic': self.topics_saved[0]},
                         {'id': 6, 'text': "Rainstorm", 'topic': self.topics_saved[0]}]

        self.messages_saved = []
        for msg in self.messages:
            temp_msg = Message.objects.create(**msg)
            self.messages_saved.append(temp_msg)

    def test_update_message_text(self):

        # create messages to update and change Topics object to id
        new_text = 'The worst weather ever'

        msg_after_update = dict(MessageSerializer(instance=self.messages_saved[0]).data)
        msg_after_update['text'] = new_text

        msg_to_send = dict(msg_after_update)
        del msg_to_send['created_at']

        factory = APIRequestFactory()
        message_view = MessageViewSet.as_view({'put': 'update'})
        request = factory.put(reverse('messages-detail', args=(self.messages[0]['id'],)), msg_to_send)
        response = message_view(request, pk=1)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), msg_after_update)
        self.assertEqual(response['content-type'], 'application/json')

    def test_update_message_with_too_short_text(self):

        # create messages to update and change Topics object to id
        new_text = 'H'*9

        msg_after_update = dict(MessageSerializer(instance=self.messages_saved[0]).data)
        msg_after_update['text'] = new_text

        msg_to_send = dict(msg_after_update)
        del msg_to_send['created_at']

        factory = APIRequestFactory()
        message_view = MessageViewSet.as_view({'put': 'update'})
        request = factory.put(reverse('messages-detail', args=(self.messages[0]['id'],)), msg_to_send)
        response = message_view(request, pk=1)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {'text': ['Ensure this value has at least 10 characters (it has 9).']})
        self.assertEqual(response['content-type'], 'application/json')

    def test_update_message_text_with_additionals_attr(self):

        # create messages to update and change Topics object to id
        new_text = 'The worst weather ever'

        msg_after_update = dict(MessageSerializer(instance=self.messages_saved[0]).data)
        msg_after_update['text'] = new_text

        msg_to_send = dict(msg_after_update)
        del msg_to_send['created_at']
        msg_to_send['add_attr'] = 'New Value'

        factory = APIRequestFactory()
        message_view = MessageViewSet.as_view({'put': 'update'})
        request = factory.put(reverse('messages-detail', args=(self.messages[0]['id'],)), msg_to_send)
        response = message_view(request, pk=1)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), msg_after_update)
        self.assertEqual(response['content-type'], 'application/json')

    def test_views_cant_update_message_topic(self):

        msg_after_update = dict(MessageSerializer(instance=self.messages_saved[0]).data)
        msg_after_update['topic'] = 2

        msg_to_send = dict(msg_after_update)
        del msg_to_send['created_at']

        factory = APIRequestFactory()
        message_view = MessageViewSet.as_view({'put': 'update'})
        request = factory.put(reverse('messages-detail', args=(self.messages[0]['id'],)), msg_to_send)
        response = message_view(request, pk=1)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {'topic': ['Cannot update message topic']})
        self.assertEqual(response['content-type'], 'application/json')

class MessageViewsDeleteMessages(TestCase):

    def test_delete_nonexisting_message(self):
        factory = APIRequestFactory()
        msg_view = MessageViewSet.as_view({'delete': 'destroy'})
        request = factory.delete(reverse('messages-detail', args=(1,)))
        response = msg_view(request, pk=1)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {'detail': 'Not found.'})
        self.assertEqual(response['content-type'], 'application/json')

    def test_delete_existing_topic(self):

        self.topics = [{'id': 1, 'title': 'What is the weather like?'}, {'id': 2, 'title': 'The Most Popular Color in the World'},
                       {'id': 3, 'title': 'The best programming language'}, {'id': 4, 'title': '10 Best Programming Language to Learn in 2020'}]
        self.topics_saved = []
        for topic in self.topics:
            self.topics_saved.append(Topic.objects.create(**topic))

        self.messages = [{'id': 1, 'text': "Hot and sunny day", 'topic': self.topics_saved[0]},
                         {'id': 2, 'text': "Blue", 'topic': self.topics_saved[1]},
                         {'id': 3, 'text': "Python", 'topic': self.topics_saved[2]}]

        self.messages_saved = []
        for msg in self.messages:
            temp_msg = Message.objects.create(**msg)
            self.messages_saved.append(temp_msg)

        factory = APIRequestFactory()
        msg_view = MessageViewSet.as_view({'delete': 'destroy'})
        request = factory.delete(reverse('messages-detail', args=(2,)))
        response = msg_view(request, pk=1)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        factory = APIRequestFactory()
        msg_view = MessageViewSet.as_view({'delete': 'destroy'})
        request = factory.delete(reverse('messages-detail', args=(1,)))
        response = msg_view(request, pk=1)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {'detail': 'Not found.'})
        self.assertEqual(response['content-type'], 'application/json')