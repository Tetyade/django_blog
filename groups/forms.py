from django import forms
from messages.forms import MessageForm as BaseMessageForm
from .models import Message, Group
from django.contrib.auth import get_user_model
from auth_system.models import Follow

User = get_user_model()

class MessageForm(BaseMessageForm):
    class Meta(BaseMessageForm.Meta):
        model = Message

class GroupCreateForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Додати учасників"
    )

    class Meta:
        model = Group
        fields = ['name', 'members']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        data = kwargs.pop('data', None)
        super().__init__(*args, **kwargs)

        # Взаємні фоловери
        mutual_followers = user.following_set.filter(following__following_set__following=user)

        # Фільтр по username, якщо є GET-параметр search
        if data and data.get('search'):
            search = data.get('search').strip()
            mutual_followers = mutual_followers.filter(username__icontains=search)

        self.fields['members'].queryset = mutual_followers


class GroupCreateForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),  # спочатку порожній queryset
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Додати учасників (тільки взаємні підписки)"
    )

    class Meta:
        model = Group
        fields = ['name', 'members']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # отримуємо поточного користувача
        super().__init__(*args, **kwargs)

        # отримуємо користувачів з взаємною підпискою
        mutual_following = User.objects.filter(
            id__in=Follow.objects.filter(follower=user)
                                   .values_list('following', flat=True)
        ).filter(
            id__in=Follow.objects.filter(following=user)
                                   .values_list('follower', flat=True)
        )
        self.fields['members'].queryset = mutual_following

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'members']
        widgets = {
            'members': forms.CheckboxSelectMultiple
        }