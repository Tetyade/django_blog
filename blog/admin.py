from django.contrib import admin

from blog.models import Post, Authors

admin.site.register(Post)
admin.site.register(Authors)
