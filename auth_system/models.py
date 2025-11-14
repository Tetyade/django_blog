import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

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
