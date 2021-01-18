from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Post(models.Model):   

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, default=None)  
    authors = models.TextField(max_length=500, default=None)
    subjects = models.TextField(max_length=500, default=None)
    bookshelves = models.TextField(max_length=500, default=None)
    languages = models.TextField(max_length=500, default=None)
    copyright = models.TextField(max_length=500, default=None)
    content_url = models.URLField(max_length=200, blank=True, null=True, default=None)
    download_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return '%s' % self.title