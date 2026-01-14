import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.conf import settings

User = settings.AUTH_USER_MODEL

def validate_image(image):
    # Перевірка розміру файлу
    max_size_mb = 3
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Зображення перевищує {max_size_mb}MB.")

    # Перевірка типу файлу
    valid_mime_types = ['image/jpeg', 'image/png', 'image/webp']
    file_mime_type = image.file.content_type
    if file_mime_type not in valid_mime_types:
        raise ValidationError("Дозволені лише JPEG, PNG або WebP файли.")

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, validators=[validate_image])

    def __str__(self):
        return self.username
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('auth_system:profile', args=[str(self.uuid)])
    
class Follow(models.Model):
    follower = models.ForeignKey(User, related_name="following_set", on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name="followers_set", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.follower} → {self.following}"
