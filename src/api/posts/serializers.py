from rest_framework import serializers as ser

from apps.posts.models import (Album, AlbumTag, Media, MediaTag, PollChoice, Post, PostTag, Privacy, Story)
from ..accounts.serializers import UserDisplaySerializer, UserGroupSerializer


class PrivacyModelSerializer(ser.ModelSerializer):
    # exclude = UserDisplaySerializer(read_only=True, many=True)
    # include = UserDisplaySerializer(read_only=True, many=True)

    class Meta:
        model = Privacy
        fields = "__all__"


class MediaModelSerializer(ser.ModelSerializer):
    class Meta:
        model = Media
        fields = "__all__"


class ParentPostSerializer(ser.ModelSerializer):
    user = UserDisplaySerializer(read_only=True)
    group = UserGroupSerializer(read_only=True)
    tags = UserDisplaySerializer(many=True, read_only=True)
    media = MediaModelSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = "__all__"


class PostModelSerializer(ser.ModelSerializer):
    user = UserDisplaySerializer(read_only=True)
    group = UserGroupSerializer(read_only=True)
    tags = UserDisplaySerializer(many=True, read_only=True)
    parent = ParentPostSerializer(read_only=True)
    liked = UserDisplaySerializer(many=True)

    class Meta:
        model = Post
        fields = "__all__"


class PostCreateSerializer(ser.ModelSerializer):
    parent_id = ser.IntegerField(required=False)
    # shared_user_id = ser.IntegerField(required=False)
    files = MediaModelSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ("content", "mood", "share_a_link", "post_type", "location",
                  "share_type", "files", "is_parent", "parent_id",
                  "shared_user", "is_share", "shared_group",)

    def validate(self, attrs):
        is_parent = attrs.get("is_parent", False)
        parent_id = attrs.get("parent_id", "")
        if is_parent and parent_id == "":
            raise ser.ValidationError({"parent_id": "a parent post must be associated"})
        return attrs

    def create(self, validated_data):
        files = validated_data.pop("files", [])
        user = self.context.get("user")
        parent_id = self.validated_data.get("parent_id", None)
        location = validated_data.get("location", "")
        shared_link = validated_data.get("share_a_link", "")
        shared_user = validated_data.get("shared_user", None)
        shared_group = validated_data.get("shared_group", None)
        share_type = validated_data.get("share_type", "")
        mood = validated_data.get("mood", "")
        content = validated_data.get("content", "")
        is_share = validated_data.get("is_share", False)
        if validated_data["post_type"] == "user":
            post = Post.objects.create_user_post(
                user=user,
                files=list(files),
                parent_id=parent_id,
                link=shared_link,
                shared_user=shared_user,
                location=location,
                share_type=share_type,
                mood=mood,
                content=content,
                is_share=is_share
            )
        elif validated_data["post_type"] == "group":
            post = Post.objects.create_group_post(
                user=user,
                group=shared_group,
                mood=mood,
                content=content,
                is_share=is_share,
                share_type=share_type,
                parent_id=parent_id,
                location=location,
                link=shared_link,
                files=list(files)
            )
        else:
            post = Post.objects.create_poll_post(
                user=user,
                content=content, link=shared_link,
                location=location
            )
        return post


class PostTagModelSerializer(ser.ModelSerializer):
    class Meta:
        model = PostTag
        fields = ("post", "tagged_user")

    def validate(self, attrs):
        if attrs["post"] is None:
            raise ser.ValidationError({"post": "This field is required"})
        elif attrs["tagged_user"] is None:
            raise ser.ValidationError({"user": "Please tag a user"})
        return attrs

    def create(self, validated_data):
        return PostTag.objects.create(**validated_data)


class StoryModelSerializer(ser.ModelSerializer):
    media = MediaModelSerializer(many=True)

    class Meta:
        model = Story
        fields = ("media", "timestamp")


class AlbumModelSerializer(ser.ModelSerializer):
    user = UserDisplaySerializer(read_only=True)
    tagged_user = UserDisplaySerializer(read_only=True, many=True)
    privacy = PrivacyModelSerializer()

    class Meta:
        model = Album
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.location = validated_data.get("location", instance.location)
        instance.date = validated_data.get("date", instance.date)
        instance.save()
        privacy = instance.privacy
        privacy_data = validated_data.pop("privacy")
        privacy.is_public = privacy_data.get("is_public", privacy.is_public)
        privacy.is_private = privacy_data.get("is_private", privacy.is_private)
        privacy.friends = privacy_data.get("friends", privacy.friends)
        privacy.exclude = privacy_data.get("exclude", privacy.exclude)
        privacy.include = privacy_data.get("include", privacy.include)
        privacy.save()
        return instance


class AlbumCreateSerializer(ser.ModelSerializer):
    privacy = PrivacyModelSerializer()
    photos = MediaModelSerializer(many=True)

    class Meta:
        model = Album
        fields = ("name", "photos", "description", "location", "date", "published", "privacy")

    def validate(self, attrs):
        if attrs["name"] == "":
            raise ser.ValidationError({"name": "Album needs a name"})
        return attrs

    def create(self, validated_data):
        _privacy = validated_data.pop("privacy", None)
        privacy = Privacy.objects.create(**_privacy)
        photos = validated_data.pop("photos", None)
        return Album.objects.add_album(
            user=self.context["request"].user,
            privacy=privacy,
            photos=photos,
            date=validated_data["date"],
            name=validated_data["name"],
            location=validated_data["location"],
            description=validated_data["description"],
            published=validated_data["published"]
        )


class PollChoiceModelSerializer(ser.ModelSerializer):
    vote_percent = ser.SerializerMethodField()
    voted = ser.SerializerMethodField()
    votes = UserDisplaySerializer(many=True, read_only=True)

    class Meta:
        model = PollChoice
        fields = ("id", "choice", "votes", "vote_percent", "voted")

    def get_vote_percent(self, obj):
        return PollChoice.objects.calculate(poll_id=obj.id)

    def get_voted(self, obj):
        return obj.voted(user=self.context["request"].user)


class PollChoiceCreateSerializer(ser.ModelSerializer):
    post_id = ser.IntegerField()

    class Meta:
        model = PollChoice
        fields = ("choice", "post_id")

    def validate(self, attrs):
        if not attrs["choice"]:
            raise ser.ValidationError({"choice": "This field is required"})
        if not attrs["post_id"]:
            raise ser.ValidationError({"post_id": "Please select a post"})
        return attrs

    def create(self, validated_data):
        return PollChoice.objects.add_poll_choice(post_id=validated_data["post_id"],
                                                  choice=validated_data["choice"])


class MediaTagModelSerializer(ser.ModelSerializer):
    class Meta:
        model = MediaTag
        fields = ("media", "user")

    def validate(self, attrs):
        if attrs["media"] is None:
            raise ser.ValidationError({"media": "This field is required"})
        if not attrs["user"]:
            raise ser.ValidationError({"user": "Please select a user"})
        return attrs

    def create(self, validated_data):
        return MediaTag.objects.create(**validated_data)


class AlbumTagSerializer(ser.ModelSerializer):
    class Meta:
        model = AlbumTag
        fields = ("album", "user")

    def validate(self, attrs):
        if attrs["album"] is None:
            raise ser.ValidationError({"album": "This field is required"})
        if not attrs["user"]:
            raise ser.ValidationError({"user": "Please select a user"})
        return attrs

    def create(self, validated_data):
        return AlbumTag.objects.create(**validated_data)


class PostLikeSerializer(ser.Serializer):
    post_id = ser.IntegerField(required=True)


class PollVoteSerializer(ser.Serializer):
    poll_id = ser.IntegerField(required=True)