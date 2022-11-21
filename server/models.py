from django.db import models

class User(models.Model):
    username = models.CharField(unique=True, max_length=20)
    password = models.CharField(max_length=99)