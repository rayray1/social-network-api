from django.db import models
from django.contrib.auth.models import AbstractUser


class SocialUser(AbstractUser, models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Post(models.Model):
    user = models.ForeignKey(SocialUser, related_name='posts', on_delete=models.CASCADE)
    title = models.TextField(unique=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    liked = models.IntegerField(default=0)
    unliked = models.IntegerField(default=0)

    def __str__(self):
        return self.title
