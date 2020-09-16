from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from rest_framework import status
from chat.models import Topic
from chat.views import TopicViewSet
from unittest import mock
import json
import datetime
import pytz


class TopicViewsALLTests(TestCase):

    def test_view_empty_list_all_topics(self):
        factory = APIRequestFactory()
        topic_view = TopicViewSet.as_view({'get': 'list'})
        request = factory.get(reverse('topics-list'))
        response = topic_view(request)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), [])
        self.assertEqual(response['content-type'], 'application/json')

    def test_view_with_some_topics(self):
        mocked = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.topics = [{'id': 1, 'title': 'What is the weather like?'}, {'id': 2, 'title': 'The Most Popular Color in the World'},
                       {'id': 3, 'title': 'The best programming language'}, {'id': 4, 'title': '10 Best Programming Language to Learn in 2020'}]
        self.topics_data = []
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            for topic in self.topics:
                Topic.objects.create(**topic)
                temp_topic = topic
                temp_topic['created_at'] = '2020-01-01T00:00:00Z'
                self.topics_data.append(temp_topic)

        factory = APIRequestFactory()
        topic_view = TopicViewSet.as_view({'get': 'list'})
        request = factory.get(reverse('topics-list'))
        response = topic_view(request)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), self.topics)
        self.assertEqual(response['content-type'], 'application/json')


class TopicViewsGetDetailTests(TestCase):

    def test_get_details_nonexisting_topic(self):

        factory = APIRequestFactory()
        topic_view = TopicViewSet.as_view(actions={'get': 'retrieve'})

        request = factory.get(reverse('topics-detail', args=(1,)))
        response = topic_view(request, pk=1)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {'detail': 'Not found.'})
        self.assertEqual(response['content-type'], 'application/json')

    def test_get_details_existing_topic(self):

        mocked = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.topics = [{'id': 1, 'title': 'What is the weather like?'}, {'id': 2, 'title': 'The Most Popular Color in the World'},
                       {'id': 3, 'title': 'The best programming language'}, {'id': 4, 'title': '10 Best Programming Language to Learn in 2020'}]
        self.topics_data = []
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            for topic in self.topics:
                Topic.objects.create(**topic)
                temp_topic = topic
                temp_topic['created_at'] = '2020-01-01T00:00:00Z'
                self.topics_data.append(temp_topic)

        factory = APIRequestFactory()
        topic_view = TopicViewSet.as_view(actions={'get': 'retrieve'})

        request = factory.get(reverse('topics-detail', args=(3,)))
        response = topic_view(request, pk=3)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), self.topics_data[2])
        self.assertEqual(response['content-type'], 'application/json')


class TopicViewsCreateTopics(TestCase):

    def test_create_topic_with_correct_data(self):
        mocked = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.topic = {'id': 1, 'title': 'What is the weather like?'}

        factory = APIRequestFactory()
        topic_view = TopicViewSet.as_view(actions={'post': 'create'})

        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            request = factory.post(reverse('topics-list'), self.topic)
            response = topic_view(request)
            response.render()

            temp_topic = self.topic
            temp_topic['created_at'] = '2020-01-01T00:00:00Z'
            self.topic_data = temp_topic

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), self.topic_data)
        self.assertEqual(response['content-type'], 'application/json')

    def test_create_topic_with_incorrect_data(self):
        mocked = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.topic = {'id': 1, 'title': 'What is the weather like?'}
        self.topic_with_additional_attr = {'id': 1, 'title': 'What is the weather like?', 'additional': 'attribute'}
        factory = APIRequestFactory()
        topic_view = TopicViewSet.as_view(actions={'post': 'create'})

        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            request = factory.post(reverse('topics-list'), self.topic)
            response = topic_view(request)
            response.render()

            temp_topic = self.topic
            temp_topic['created_at'] = '2020-01-01T00:00:00Z'
            self.topic_data = temp_topic

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), self.topic)
        self.assertEqual(response['content-type'], 'application/json')

    def test_create_topic_with_too_short_title(self):
        mocked = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.topic = {'id': 1, 'title': 'W'*4}

        factory = APIRequestFactory()
        topic_view = TopicViewSet.as_view(actions={'post': 'create'})

        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            request = factory.post(reverse('topics-list'), self.topic)
            response = topic_view(request)
            response.render()

            temp_topic = self.topic
            temp_topic['created_at'] = '2020-01-01T00:00:00Z'
            self.topic_data = temp_topic

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content),  {'title': ['Ensure this field has at least 5 characters.']})
        self.assertEqual(response['content-type'], 'application/json')

    def test_create_topic_with_too_long_title(self):
        mocked = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.topic = {'id': 1, 'title': 'W'*256}

        factory = APIRequestFactory()
        topic_view = TopicViewSet.as_view(actions={'post': 'create'})

        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            request = factory.post(reverse('topics-list'), self.topic)
            response = topic_view(request)
            response.render()

            temp_topic = self.topic
            temp_topic['created_at'] = '2020-01-01T00:00:00Z'
            self.topic_data = temp_topic

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content),  {'title': ['Ensure this field has no more than 255 characters.']})
        self.assertEqual(response['content-type'], 'application/json')


class TopicViewsUpdateTopics(TestCase):

    def test_update_nonexisting_topic(self):
        factory = APIRequestFactory()
        topic_view = TopicViewSet.as_view({'put': 'update'})
        request = factory.put(reverse('topics-detail', args=(1,)))
        response = topic_view(request, pk=1)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {'detail': 'Not found.'})
        self.assertEqual(response['content-type'], 'application/json')

    def test_update_existing_topic(self):
        mocked = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        mocked_date_month_later = datetime.datetime(2020, 2, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.topics = [{'id': 1, 'title': 'What is the weather like?'}, {'id': 2, 'title': 'The Most Popular Color in the World'},
                       {'id': 3, 'title': 'The best programming language'}, {'id': 4, 'title': '10 Best Programming Language to Learn in 2020'}]
        self.topics_data = []
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            for topic in self.topics:
                Topic.objects.create(**topic)
                temp_topic = topic
                temp_topic['created_at'] = '2020-01-01T00:00:00Z'
                self.topics_data.append(temp_topic)

        self.topics[2]['title'] = 'New the best title'

        factory = APIRequestFactory()
        topic_view = TopicViewSet.as_view({'put': 'update'})
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_date_month_later)):
            request = factory.put(reverse('topics-detail', args=(3,)), {'title': self.topics[2]['title']})
            response = topic_view(request, pk=3)
            response.render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), self.topics[2])
        self.assertEqual(response['content-type'], 'application/json')

    def test_update_existing_topic_with_too_short_title(self):
        mocked = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        mocked_date_month_later = datetime.datetime(2020, 2, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.topics = [{'id': 1, 'title': 'What is the weather like?'},
                       {'id': 2, 'title': 'The Most Popular Color in the World'},
                       {'id': 3, 'title': 'The best programming language'},
                       {'id': 4, 'title': '10 Best Programming Language to Learn in 2020'}]
        self.topics_data = []
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            for topic in self.topics:
                Topic.objects.create(**topic)
                temp_topic = topic
                temp_topic['created_at'] = '2020-01-01T00:00:00Z'
                self.topics_data.append(temp_topic)

        self.topics[2]['title'] = 'T' * 4

        factory = APIRequestFactory()
        topic_view = TopicViewSet.as_view({'put': 'update'})
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_date_month_later)):
            request = factory.put(reverse('topics-detail', args=(3,)), {'title': self.topics[2]['title']})
            response = topic_view(request, pk=3)
            response.render()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {'title': ['Ensure this field has at least 5 characters.']})
        self.assertEqual(response['content-type'], 'application/json')

    def test_update_existing_topic_with_too_long_title(self):
        mocked = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        mocked_date_month_later = datetime.datetime(2020, 2, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.topics = [{'id': 1, 'title': 'What is the weather like?'},
                       {'id': 2, 'title': 'The Most Popular Color in the World'},
                       {'id': 3, 'title': 'The best programming language'},
                       {'id': 4, 'title': '10 Best Programming Language to Learn in 2020'}]
        self.topics_data = []
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            for topic in self.topics:
                Topic.objects.create(**topic)
                temp_topic = topic
                temp_topic['created_at'] = '2020-01-01T00:00:00Z'
                self.topics_data.append(temp_topic)

        self.topics[2]['title'] = 'T' * 256

        factory = APIRequestFactory()
        topic_view = TopicViewSet.as_view({'put': 'update'})
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_date_month_later)):
            request = factory.put(reverse('topics-detail', args=(3,)), {'title': self.topics[2]['title']})
            response = topic_view(request, pk=3)
            response.render()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {'title': ['Ensure this field has no more than 255 characters.']})
        self.assertEqual(response['content-type'], 'application/json')

    def test_update_existing_topic_with_too_many_attr(self):
        mocked = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        mocked_date_month_later = datetime.datetime(2020, 2, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.topics = [{'id': 1, 'title': 'What is the weather like?'},
                       {'id': 2, 'title': 'The Most Popular Color in the World'},
                       {'id': 3, 'title': 'The best programming language'},
                       {'id': 4, 'title': '10 Best Programming Language to Learn in 2020'}]
        self.topics_data = []
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            for topic in self.topics:
                Topic.objects.create(**topic)
                temp_topic = topic
                temp_topic['created_at'] = '2020-01-01T00:00:00Z'
                self.topics_data.append(temp_topic)

        self.topics[2]['title'] = '10 Best Programming Language to Learn in 2020'

        factory = APIRequestFactory()
        topic_view = TopicViewSet.as_view({'put': 'update'})
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_date_month_later)):
            request = factory.put(reverse('topics-detail', args=(3,)), {'title': self.topics[2]['title'], 'additional': 'attr'})
            response = topic_view(request, pk=3)
            response.render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), self.topics[2])
        self.assertEqual(response['content-type'], 'application/json')

class TopicViewsDeleteTopics(TestCase):

    def test_delete_nonexisting_topic(self):
        factory = APIRequestFactory()
        topic_view = TopicViewSet.as_view({'delete': 'destroy'})
        request = factory.delete(reverse('topics-detail', args=(1,)))
        response = topic_view(request, pk=1)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {'detail': 'Not found.'})
        self.assertEqual(response['content-type'], 'application/json')

    def test_delete_existing_topic(self):

        mocked = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        self.topics = [{'id': 1, 'title': 'What is the weather like?'}, {'id': 2, 'title': 'The Most Popular Color in the World'},
                       {'id': 3, 'title': 'The best programming language'}, {'id': 4, 'title': '10 Best Programming Language to Learn in 2020'}]
        self.topics_data = []
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            for topic in self.topics:
                Topic.objects.create(**topic)
                temp_topic = topic
                temp_topic['created_at'] = '2020-01-01T00:00:00Z'
                self.topics_data.append(temp_topic)

        factory = APIRequestFactory()
        topic_view = TopicViewSet.as_view({'delete': 'destroy'})
        request = factory.delete(reverse('topics-detail', args=(2,)))
        response = topic_view(request, pk=2)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        factory = APIRequestFactory()
        topic_view = TopicViewSet.as_view(actions={'get': 'retrieve'})

        request = factory.get(reverse('topics-detail', args=(2,)))
        response = topic_view(request, pk=2)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {'detail': 'Not found.'})
        self.assertEqual(response['content-type'], 'application/json')