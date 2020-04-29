from django.urls import path
from .views import CommentCreateAPIView, CommentDetailView

app_name = "comment-api"

urlpatterns = [
    path("add/", CommentCreateAPIView.as_view()),
    path("<int:id>", CommentDetailView.as_view(), name="comment-detail"),
]