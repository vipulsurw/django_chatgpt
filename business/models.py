from django.db import models

# Create your models here.
class Conversation(models.Model):
    sender = models.CharField(max_length=15)
    message = models.CharField(max_length=2000)
    response = models.CharField(max_length=2000)