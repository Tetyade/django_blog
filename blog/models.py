from django.db import models

class Authors(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Authors, on_delete=models.CASCADE, related_name='posts')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

