from django.contrib.contenttypes.models import ContentType
from rest_framework.serializers import ModelSerializer, ValidationError, SerializerMethodField
from apps.comments.models import Comment
from ..accounts.serializers import UserDisplaySerializer


def comment_create_func(model_type="post", id=None, parent_id=None, user=None):
    class CommentCreateSerializer(ModelSerializer):
        class Meta:
            model = Comment
            fields = ('content', "comment_type", "media")

        def __init__(self, **kwargs):
            self.model_type = model_type
            self.id = id
            self.parent_obj = None
            self.user = user
            if parent_id:
                parent = Comment.objects.get(id=parent_id)
                if parent:
                    self.parent_obj = parent
            super(CommentCreateSerializer, self).__init__(**kwargs)

        def validate(self, attrs):
            model = ContentType.objects.get(model=self.model_type)
            if model is None:
                raise ValidationError(
                    {"object": f"The {self.model_type} you are commenting on does no longer exist"})
            model = model.model_class()
            obj = model.objects.get(id=self.id)
            if obj is None:
                raise ValidationError({f"{self.model_type}": "This object does not exist"})
            if attrs["comment_type"] == "text" and attrs["content"] == "":
                raise ValidationError({"content": "Please make a valid comment"})
            if attrs["comment_type"] == "sticker" or attrs["comment_type"] == "image" \
                    and attrs["media"] is None:
                raise ValidationError({"comment_type": "Please upload a media file"})
            return attrs

        def create(self, validated_data):
            return Comment.objects.create_by_model_type(
                id=self.id, content=validated_data["content"],
                comment_type=validated_data["comment_type"], media=validated_data["media"],
                parent_obj=self.parent_obj, model_type=self.model_type, user=self.user
            )

    return CommentCreateSerializer


class CommentChildSerializer(ModelSerializer):
    user = UserDisplaySerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'user', 'content', 'comment_type', 'media', 'timestamp')


class CommentDetailSerializer(ModelSerializer):
    user = UserDisplaySerializer(read_only=True)
    reply_count = SerializerMethodField()
    # content_object_url = ser.SerializerMethodField()
    replies = SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "user", "content", 'comment_type', 'media', "reply_count", "replies", "timestamp")
        read_only_fields = [
            "reply_count",
            "replies",
        ]

    def get_replies(self, obj):
        if obj.is_parent:
            return CommentChildSerializer(obj.children, many=True).data
        return []

    def get_reply_count(self, obj):
        if obj.is_parent:
            return obj.children.count()
        return 0
