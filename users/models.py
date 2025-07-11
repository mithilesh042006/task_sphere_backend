from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string


def generate_user_id():
    """Generate a unique 8-digit alphanumeric user ID"""
    while True:
        user_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        # Check if User model exists and table is created
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users_user';")
                if cursor.fetchone() is None:
                    return user_id  # Table doesn't exist yet, return any ID

            if not User.objects.filter(user_id=user_id).exists():
                return user_id
        except:
            return user_id  # If any error, just return the generated ID


class User(AbstractUser):
    """Custom User model with 8-digit alphanumeric ID"""
    user_id = models.CharField(
        max_length=8,
        unique=True,
        blank=True,
        help_text="Unique 8-digit alphanumeric identifier"
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Override username to use email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user_id})"

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = generate_user_id()
        super().save(*args, **kwargs)
