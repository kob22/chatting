from django.db import models
from django.core.validators import MinLengthValidator


class Topic(models.Model):
    title = models.CharField(max_length=255, validators=[MinLengthValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)