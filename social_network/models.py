from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser, models.Model):
    interests = models.CharField(max_length=1000, null=True)
    about_me = models.CharField(max_length=1000, null=True)
    phone = models.CharField(max_length=20, null=True)
    city = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.username


class Post(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    like = models.PositiveIntegerField(default=0)
    dislike = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.text
