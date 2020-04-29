from django.db.models import Q
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from apps.chat.models import Thread
from .serializers import ThreadModelSerializer, ThreadCreateSerializer


class ThreadListAPIView(ListAPIView):
    serializer_class = ThreadModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Thread.objects.by_user(self.request.user)
        data = self.request.query_params.get
        if data("user"):
            qs = qs.filter(
                Q(second__username__icontains=data("user")) |
                Q(first__username__icontains=data("user"))
            )
        if data("date"):
            qs = qs.filter(
                Q(timestamp=data("date"))
            )
        return qs


class NewThreadAPIView(CreateAPIView):
    serializer_class = ThreadCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Thread.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)