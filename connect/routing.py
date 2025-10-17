# your_app/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/posts/(?P<post_id>\d+)/votes/$', consumers.VoteConsumer.as_asgi()),
]