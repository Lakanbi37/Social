from django.db.models import Q
from rest_framework import filters, generics, permissions
from apps.posts.models import Post
from core.utils.permissions import IsOwnerOrReadOnly
from .serializers import *


class CommentCreateAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Comment.objects.all()

    def get_serializer_class(self):
        model_type = self.request.GET.get("model_type")
        id = self.request.GET.get("id")
        parent_id = self.request.GET.get("parent_id", None)
        return comment_create_func(
            model_type=model_type, id=id,
            parent_id=parent_id, user=self.request.user
        )


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentDetailSerializer
    queryset = Comment.objects.filter(id__gte=0)
    permission_classes = [IsOwnerOrReadOnly]
    lookup_field = "id"


class PostCommentListAPIView(generics.ListAPIView):
    serializer_class = CommentDetailSerializer
    permission_classes = [permissions.AllowAny]
    # pagination_class = StandardResultPagination
    filter_backends = [filters.OrderingFilter]
    # search_fields = ["content", "user__username", "user__first_name", "user__last_name"]

    def get_object(self):
        obj = generics.get_object_or_404(Post.objects.all(), id=self.kwargs.get("post_id"))
        return obj

    def get_queryset(self):
        qs = self.get_object().comments
        data = self.request.query_params.get
        if data("content"):
            qs = qs.filter(Q(content__icontains=data("content")))
        if data("user"):
            qs = qs.filter(Q(user__username__icontains=data("user")))
        if data("type"):
            qs = qs.filter(Q(comment_type__iexact=data("type")))
        if data("first_name"):
            qs = qs.filter(Q(user__first_name__icontains=data("first_name")))
        if data("last_name"):
            qs = qs.filter(Q(user__last_name__icontains=data("last_name")))
        return qs

