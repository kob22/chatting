from django.test import TestCase
from chat.models import Topic
from django.core.exceptions import ValidationError


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
