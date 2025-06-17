from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True)
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    password = models.CharField(max_length=128, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

        db_table = 'Users'

        def __str__(self):
            return self.email
        
    