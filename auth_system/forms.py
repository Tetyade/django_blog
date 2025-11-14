from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from auth_system.models import CustomUser
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('bio', 'profile_picture')

class RegisterForm(CustomUserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length = 30, required=False)
    last_name = forms.CharField(max_length = 30, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    profile_picture = forms.ImageField(required=False)


    # class Meta:
    #     model = CustomUser
    #     fields = ("first_name", "last_name", "username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError("Email already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()
        user.username = self.cleaned_data["username"].lower()
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.bio = self.cleaned_data["bio"]
        user.profile_picture = self.cleaned_data.get("profile_picture")
        if commit:
            user.save()
        return user
