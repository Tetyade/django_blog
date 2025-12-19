from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        labels = {
            "content": "",
        }
        widgets = {
            "content": forms.Textarea(attrs={
                "rows": 2,
                "placeholder": "Write here...",
                "style": (
                    "width:100%; "          # повна ширина
                    "padding:12px; "
                    "border-radius:14px; "
                    "border:1px solid #ccc; "
                    "font-size:14px; "
                    "font-family:inherit; "
                    "resize:none; "
                    "box-sizing:border-box;"  # враховує padding у ширину
                )
            }),
        }
