"""chatting URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from chat import views as chat_views

router = routers.DefaultRouter()
router.register(r'topics', chat_views.TopicViewSet, basename='topics')
router.register(r'messages', chat_views.MessageViewSet, basename='messages')

message_from_topic_list = chat_views.MessageFromTopicViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
message_from_topic_detail = chat_views.MessageFromTopicViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('topics/<int:topic_id>/messages/', message_from_topic_list, name='message-from-topic-list'),
    path('topics/<int:topic_id>/messages/<int:msg_id>/', message_from_topic_detail, name='message-from-topic-detail'),

]
