from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone

class Post(models.Model):
    header = models.CharField(max_length=255)
    text = models.TextField()
    time = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', default = '')

    class Meta:
        ordering = ['-id']


class Subscriber(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author', default = '')
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriber', default = '')

    class Meta:
        unique_together = (("author", "subscriber"),)


class Read(models.Model):
    reader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reader', default = '')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post', default = '')

    class Meta:
        unique_together = (("reader", "post"),)
