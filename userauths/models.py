import random
import string

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'Customer'),
        (2, 'Vendor'),
        (3, 'Admin'),
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    bio = models.CharField(max_length=100, blank=True)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=1)

    # Required fields for AbstractUser
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def is_vendor(self):
        return self.user_type == 2

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_verification_code(self):
        """Generate a 6-digit verification code."""
        return ''.join(random.choices(string.digits, k=6))

    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = self.generate_verification_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Profile for {self.user.username}"
    
#############Contact us #####################
class ContactUs(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    message =models.TextField()

    class Meta:
        verbose_name = "Contact Us"
        verbose_name_plural= "Contact Us"
    def __str__(self):
        return self.name