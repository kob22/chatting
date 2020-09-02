from django.db import models
from django.core.validators import MinLengthValidator


class Topic(models.Model):
    title = models.CharField(max_length=255, validators=[MinLengthValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
