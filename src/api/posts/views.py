from rest_framework import generics, status, permissions, response
from .serializers import *
from apps.accounts.mixins import ProfileObjectMixin
from ..mixins import CreateListModelMixin


class PostCreateAPIView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        ctx = super(PostCreateAPIView, self).get_serializer_context()
        ctx["user"] = self.request.user
        return ctx


class PostListAPIView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostModelSerializer
    permission_classes = [permissions.AllowAny]


class PostRetrieveDestroyAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = PostModelSerializer
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"


class UserPostListAPIView(ProfileObjectMixin, generics.ListAPIView):
    serializer_class = PostModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.get_posts


class PostTagCreateAPIView(CreateListModelMixin):
    serializer_class = PostTagModelSerializer
    queryset = PostTag.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class StoryListAPIView(ProfileObjectMixin, generics.ListAPIView):
    serializer_class = StoryModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.get_viewable_stories


class StoryCreateAPIView(generics.CreateAPIView):
    queryset = Media.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MediaModelSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        if isinstance(data, list):
            serializer = self.get_serializer(data=data, many=True)
        else:
            serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        resp = serializer.data
        headers = self.get_success_headers(serializer.data)
        print(resp)
        story = Story.objects.get(profile__user=request.user)
        story.add_story(files=resp)
        return response.Response(resp, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(media_type="story")


class AlbumListAPIView(ProfileObjectMixin, generics.ListAPIView):
    serializer_class = AlbumModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.get_albums


class AlbumRetrieveDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AlbumModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Album.objects.all()
    lookup_field = "name"

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class AlbumCreateAPIView(generics.CreateAPIView):
    serializer_class = AlbumCreateSerializer
    queryset = Album.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class PollChoiceCreateAPIView(CreateListModelMixin):
    serializer_class = PollChoiceCreateSerializer
    queryset = PollChoice.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class PollChoiceListAPIView(generics.ListAPIView):
    serializer_class = PollChoiceModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PollChoice.objects.filter(post__id=self.kwargs.get("post_id"))


class AlbumTagCreateAPIView(CreateListModelMixin):
    serializer_class = AlbumTagSerializer
    queryset = AlbumTag.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class MediaTagCreateAPIView(CreateListModelMixin):
    serializer_class = MediaTagModelSerializer
    queryset = MediaTag.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class PostLikeToggleAPIView(generics.GenericAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.all()

    def get_post(self, id):
        return generics.get_object_or_404(self.get_queryset(), id=id)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, **kwargs)
        serializer.is_valid(raise_exception=True)
        post_id = serializer.validated_data.get("post_id")
        resp = self.get_post(id=post_id).like_toggle(user=request.user)
        print(resp)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class PollVotesAPIView(generics.views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PollVoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        poll_id = serializer.validated_data.get("poll_id")
        is_voted = PollChoice.objects.vote(poll_id=poll_id, user=request.user)
        _response = {
            "is_voted": is_voted,
            "data": serializer.data
        }
        return response.Response(_response, status=status.HTTP_200_OK)
