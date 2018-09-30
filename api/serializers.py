from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from api.models import SocialUser, Post


class SignUpSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=SocialUser.objects.all())])
    password = serializers.CharField(max_length=128, required=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'first_name', 'last_name', 'email', 'password',)

class SocialUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)

    class Meta:
        model = get_user_model()
        fields = ('id', 'name', 'email', 'date_joined', 'user_permissions',)

class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('__all__')
