from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    email = models.EmailField(default="null", max_length=50,unique=True)
    phone_number = models.CharField(max_length=12)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
