from django.db import models
from django.core.validators import MinLengthValidator
from django.core.exceptions import ObjectDoesNotExist

class Topic(models.Model):
    title = models.CharField(max_length=255, validators=[MinLengthValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self._state.adding is False:
            try:
                msg = Message.objects.get(id=self.id)
            except ObjectDoesNotExist:
                msg = None
            if msg is not None:
                if msg.topic.id != self.topic.id:
                    raise(ValueError('You cannot change the topic of the message'))

        super(Message, self).save(*args, **kwargs)