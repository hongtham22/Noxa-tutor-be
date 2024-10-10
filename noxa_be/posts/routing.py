# posts/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/jobpost/', consumers.JobPostConsumer.as_asgi()),
]