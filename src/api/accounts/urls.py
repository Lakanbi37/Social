from django.urls import path
from .views import *

app_name = "profile-api"

urlpatterns = [
    path("bookmarks/", BookmarkCreateView.as_view()),
    path("groups/", GroupCreateAPIView.as_view()),
    path("favourites/", FavouriteListAPIView.as_view()),
    path("recommendations/", UserRecommendationsAPIView.as_view()),
    path("<slug:username>/", UserProfileAPIView.as_view(), name="profile"),
    path("favourites/add-user/", FavouriteAddAPIView.as_view()),
    path("recommendations/recommend/", RecommendUserAPIView.as_view()),
    path("groups/<slug:slug>/", UserGroupRetrieveAPIView.as_view(), name="group"),
    path("groups/<slug:slug>/members/", GroupMemberAddAPIView.as_view()),
]