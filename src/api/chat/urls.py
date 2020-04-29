from django.urls import path
from .views import *

app_name = "chat-api"

urlpatterns = [
    path("", ThreadListAPIView.as_view()),
    path("new/", NewThreadAPIView.as_view()),
]