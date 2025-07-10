from django.contrib import admin
from .models import Post, Authors, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    inlines = [CommentInline]

admin.site.register(Authors)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
