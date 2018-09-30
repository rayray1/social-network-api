from django.urls import include, path
from django.views import generic
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

from api import views


router = routers.SimpleRouter()
router.register('users', views.UserViewSet, base_name="users")
router.register('posts', views.PostViewSet, base_name="posts")


urlpatterns = [
    path('', include(router.urls)),

    path('rest-auth/', include('rest_auth.urls')),
    path('api/auth/', include('rest_framework.urls')),

    path('sign-up/', views.signup, name="signup_user"),
    path('login/', views.login, name="login_user"),

    path('api/token-auth/', obtain_jwt_token),
    path('api/token-refresh/', refresh_jwt_token),
    path('api/token-verify/', verify_jwt_token),
]
