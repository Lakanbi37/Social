from django.db.models import Q
from rest_framework import generics, response, status, permissions, filters
from apps.accounts.models import *
from .serializers import *
from .permissions import *


class UserProfileAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "username"
    queryset = UserProfile.objects.all()

    def get_object(self):
        return generics.get_object_or_404(UserProfile.objects.all(), user__username=self.kwargs.get("username"))


class UserGroupRetrieveAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserGroupSerializer
    permission_classes = [IsGroupAdmin, permissions.IsAuthenticated]
    lookup_field = "slug"
    queryset = UserGroup.objects.all()


class GroupCreateAPIView(generics.ListCreateAPIView):
    serializer_class = UserGroupCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserGroup.objects.filter(admin=self.request.user)

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)


class GroupMemberAddAPIView(generics.ListCreateAPIView):
    serializer_class = GroupMemberSerializer
    permission_classes = [IsGroupAdmin, permissions.IsAuthenticated]

    def get_object(self):
        group = generics.get_object_or_404(UserGroup.objects.all(),
                                           slug=self.kwargs.get("slug"))
        return group

    def get_queryset(self):
        qs = Member.objects.filter(group__slug=self.kwargs.get("slug"))
        data = self.request.GET.get
        if data("username"):
            qs = qs.filter(Q(user__username=data("username")))
        if data("joined"):
            qs = qs.filter(Q(date_joined=data("joined")))
        return qs

    def perform_create(self, serializer):
        serializer.save(group=self.get_object())


class FavouriteListAPIView(generics.ListCreateAPIView):
    serializer_class = FavouriteModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "user__username"]

    def get_queryset(self):
        qs = Favourite.objects.filter(user=self.request.user)
        data = self.request.GET.get
        if data.get("username"):
            qs = qs.filter(
                Q(user__username__icontains=data("username"))|
                Q(favourites__username__icontains=data("username"))
            )
        if data.get("created"):
            qs = qs.filter(
                Q(timestamp__iexact=data("created"))
            )
        if data.get("name"):
            qs = qs.filter(Q(name__icontains=data("name")))
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavouriteAddAPIView(generics.views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsUserProfile]

    def post(self, request, *args, **kwargs):
        data = request.data
        if isinstance(kwargs.get("data", {}), list):
            serializer = FavouriteMemberAdd(data=data, many=True)
        else:
            serializer = FavouriteMemberAdd(data=data)
        serializer.is_valid(raise_exception=True)
        resp = serializer.data
        print(resp)
        return response.Response(resp, status=status.HTTP_201_CREATED)


class BookmarkCreateView(generics.ListCreateAPIView):
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated, IsUserProfile]

    def get_queryset(self):
        qs = Bookmark.objects.filter(user=self.request.user)
        data = self.request.GET.get
        if data("username"):
            qs = qs.filter(
                Q(user__username__icontains=data("username"))
            )
        if data("profile"):
            qs = qs.filter(
                Q(profile__user__username__icontains=data("profile"))
            )
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecommendUserAPIView(generics.CreateAPIView):
    serializer_class = RecommendationSerializer
    queryset = Recommendation.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class UserRecommendationsAPIView(generics.ListAPIView):
    serializer_class = RecommendationModelSerializer
    permission_classes = [permissions.IsAuthenticated, IsUserProfile]

    def get_queryset(self):
        qs = Recommendation.objects.all()
        data = self.request.GET.get("data", "")
        if data == "recommended":
            qs.filter(recommended_by=self.request.user)
        elif data == "recommendations":
            qs.filter(recommended_to=self.request.user)
        return []
