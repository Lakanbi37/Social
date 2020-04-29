from django.urls import path
from .views import *
from ..comments.views import PostCommentListAPIView

app_name = "post-api"

urlpatterns = [
    path("", PostListAPIView.as_view()),
    path("albums/", AlbumListAPIView.as_view()),
    path("add-poll/", PollChoiceCreateAPIView.as_view()),
    path("album-tag/", AlbumTagCreateAPIView.as_view()),
    path("add-to-story/", StoryCreateAPIView.as_view()),
    path("create/", PostCreateAPIView.as_view()),
    path("like/", PostLikeToggleAPIView.as_view()),
    path("media-tag/", MediaTagCreateAPIView.as_view()),
    path("posts/", UserPostListAPIView.as_view()),
    path("post-tag/", PostTagCreateAPIView.as_view()),
    path("stories/", StoryListAPIView.as_view()),
    path("<int:id>/", PostRetrieveDestroyAPIView.as_view(), name="post"),
    path("album/create/", AlbumCreateAPIView.as_view()),
    path("poll/vote/", PollVotesAPIView.as_view()),
    path("album/<slug:name>/", AlbumRetrieveDestroyAPIView.as_view(), name="album"),
    path("<int:post_id>/comments/", PostCommentListAPIView.as_view(), name="comments"),
    path("poll/<int:post_id>", PollChoiceListAPIView.as_view(), name="poll"),
]