from django.urls import path, include

app_name = "api"

urlpatterns = [
    path("comments/", include("api.comments")),
    path("conversations/", include("api.chat")),
    path("posts/", include("api.posts")),
    path("profile/", include("api.accounts")),
]
