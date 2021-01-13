from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import User, Post


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.ReadOnlyField()

    class Meta(object):
        model = User
        fields = ('id', 'email', 'person_info',
                  'date_joined', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    @staticmethod
    def validate_password(value: str) -> str:
        return make_password(value)


class PostSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = Post
        fields = ('id', 'title', 'body')