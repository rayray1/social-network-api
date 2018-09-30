from copy import deepcopy
import clearbit
from copy import deepcopy
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import detail_route, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.viewsets import ModelViewSet
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler

from api.utils import ehunter
from api.models import SocialUser, Post
from api.serializers import SignUpSerializer, SocialUserSerializer, PostSerializer



class UserViewSet(ModelViewSet):
    serializer_class = SocialUserSerializer
    queryset = SocialUser.objects.all()

class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def create(self, request, *args, **kwargs):
        request.data.update({"user": request.user.pk})
        return super(PostViewSet, self).create(request, *args, **kwargs)

    @detail_route(methods=['GET'], )
    def like(self):
        post = self.get_object()
        post.liked += 1
        post.save()

    @detail_route(methods=['GET'], )
    def unlike(self):
        post = self.get_object()
        post.unliked += 1
        post.save()
        return Response(status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    data = deepcopy(request.data)
    ehunter_response = ehunter.email_verifier(data.get("email"))
    if ehunter_response['result'] == 'undeliverable':
        return Response('Email does not exist!', status=status.HTTP_400_BAD_REQUEST)
    clearbit_response = clearbit.Enrichment.find(email=data["email"], stream=True)

    if clearbit_response.get('person'):
        data.update({
            "first_name": clearbit_response['person']['name'],
            "last_name": clearbit_response['person']['name'],
        })

    serializer = SignUpSerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
    SocialUser.objects.create_user(**serializer.validated_data)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
    if not user:
        return Response({"error": "Login failed. Incorrect username or password."},
                        status=HTTP_401_UNAUTHORIZED)
    user.save()
    payload = jwt_payload_handler(user)
    jwt_token = jwt_encode_handler(payload)
    return Response({"token": jwt_token})
