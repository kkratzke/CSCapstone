from django.db import models

# Create your models here.


class MyUser(models.Model):
    username = models.CharField(max_length=20, default=None)
    last_name = models.CharField(max_length=20, default=None)
    first_name = models.CharField(max_length=20, default=None)
    email = models.CharField(max_length=30, default=None)
    password = models.CharField(max_length=64, default=None)
