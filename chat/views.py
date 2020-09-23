from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status
from . import models
from . import serializers


class TopicViewSet(viewsets.ModelViewSet):
    queryset = models.Topic.objects.all()
    serializer_class = serializers.TopicSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = models.Message.objects.all()
    serializer_class = serializers.MessageSerializer


class MessageFromTopicViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MessageSerializer

    def get_object(self):
        """
        Returns the object the view is displaying.

        Overriden methods, filter query was cut, filtering is done in query, because of topic_id which is given in URL
        """
        queryset = self.filter_queryset(self.get_queryset())

        obj = get_object_or_404(queryset)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def list(self, request, *args, **kwargs):
        self.queryset = models.Message.objects.filter(topic=kwargs['topic_id'])
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.queryset = models.Message.objects.filter(topic=kwargs['topic_id'], id=kwargs['msg_id'])
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data.dict()
        data['topic'] = kwargs['topic_id']

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        self.queryset = models.Message.objects.filter(topic=kwargs['topic_id'], id=kwargs['msg_id'])

        data = request.data.dict()
        data['topic'] = kwargs['topic_id']

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        self.queryset = models.Message.objects.filter(topic=kwargs['topic_id'], id=kwargs['msg_id'])
        return super().destroy(self, request, *args, **kwargs)