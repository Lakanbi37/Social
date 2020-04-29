from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, ValidationError, EmailField
from apps.chat.models import Thread
from ..accounts.serializers import UserDisplaySerializer
User = get_user_model()


class ThreadModelSerializer(ModelSerializer):
    first = UserDisplaySerializer(read_only=True)
    second = UserDisplaySerializer(read_only=True)

    class Meta:
        model = Thread
        fields = ("first", "second", "created")


class ThreadCreateSerializer(ModelSerializer):
    other_username = EmailField(required=True, label="Email")

    class Meta:
        model = Thread
        fields = ["other_username"]

    def validate(self, attrs):
        if not attrs["other_username"] or attrs["other_username"] == "":
            raise ValidationError({"email": "This field is required"})
        try:
            user = User.objects.get(email=attrs["other_username"])
        except Exception as e:
            raise ValidationError({"email": f"no user exist with email '{attrs['email']}'"})
        return attrs

    def create(self, validated_data):
        return Thread.objects.get_or_new(**validated_data)
