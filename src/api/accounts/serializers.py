from django.contrib.auth import get_user_model
from rest_framework import serializers as ser

from apps.accounts.models import Bookmark, Favourite, Member, Recommendation, UserGroup, UserProfile

User = get_user_model()


class UserDisplaySerializer(ser.ModelSerializer):
    avatar = ser.SerializerMethodField()

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "avatar")

    def get_avatar(self, obj):
        try:
            return obj.profile.avatar.url
        except:
            return None


class UserProfileSerializer(ser.ModelSerializer):
    user = UserDisplaySerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ("id", "user", "account_type")


class UserGroupSerializer(ser.ModelSerializer):
    admin = UserDisplaySerializer(read_only=True)
    members = UserDisplaySerializer(many=True, read_only=True)

    class Meta:
        model = UserGroup
        fields = ("id", "name", "bio", "group_type", "avatar", "admin", "members")


class GroupMemberSerializer(ser.ModelSerializer):
    group = UserGroupSerializer(read_only=True)

    class Meta:
        model = Member
        fields = ("group", "user")

    def create(self, validated_data):
        return Member.objects.add_member(**validated_data)


class UserGroupCreateSerializer(ser.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = ("id", "name", "bio", "group_type", "avatar", "members")

    def validate(self, attrs):
        if not attrs["name"]:
            raise ser.ValidationError({"name": "Group must have a name"})
        return attrs

    def create(self, validated_data):
        return UserGroup.objects.create(**validated_data)

    def update(self, instance, validated_data):
        data = validated_data.get
        instance.name = data("name", instance.name)
        instance.bio = data("bio", instance.bio)
        instance.group_type = data("group_type", instance.group_type)
        instance.avatar = data("avatar", instance.avatar)
        instance.save()
        return instance


class FavouritesSerializer(ser.ModelSerializer):
    favourites = UserDisplaySerializer(many=True, read_only=True)

    class Meta:
        model = Favourite
        fields = ("id", "name", "favourites")


class FavouriteModelSerializer(ser.ModelSerializer):
    name = ser.CharField(required=True)
    favourites = UserDisplaySerializer(many=True, read_only=True)

    class Meta:
        model = Favourite
        fields = ("id", "name", "favourites")

        read_only_fields = ["id", "favourites"]

    def validate(self, attrs):
        f_qs = Favourite.objects.filter(name=attrs["name"])
        if f_qs.exists():
            raise ser.ValidationError({"name": "An object with that name already exists"})
        return attrs

    def create(self, validated_data):
        return Favourite.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.save()
        return instance


class FavouriteMemberAdd(ser.Serializer):
    user_id = ser.IntegerField(required=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(id=attrs["user_id"])
        except Exception as e:
            raise ser.ValidationError({"user_id": f"No user with this uid {attrs['user_id']} exists"})
        return attrs


class BookmarkSerializer(ser.ModelSerializer):
    user = UserDisplaySerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = ("profile", "created")

        read_only_fields = ["created"]

    def create(self, validated_data):
        return Bookmark.objects.bookmark(**validated_data)


class RecommendationSerializer(ser.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ("recommended_to", "recommended")

    def create(self, validated_data):
        return Recommendation.objects.create(**validated_data)


class RecommendationModelSerializer(ser.ModelSerializer):
    recommended_by = UserDisplaySerializer(read_only=True)
    recommended_to = UserDisplaySerializer(read_only=True)
    recommended = UserDisplaySerializer(read_only=True)

    class Meta:
        model = Recommendation
        fields = ("recommended_by", "recommended_to", "recommended", "timestamp")
