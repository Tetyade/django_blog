from django import forms
from .models import Post
from django.utils.html import strip_tags

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'image', 'content']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Введіть заголовок...',
                'class': 'form-input'
            }),
            'content': forms.Textarea(attrs={
                'placeholder': 'Про що ви думаєте?',
                'rows': 8
            }),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        clean_title = strip_tags(title)
        return clean_title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        clean_content = strip_tags(content)
        return clean_content