from django import forms
from messages.forms import MessageForm as BaseMessageForm
from .models import Message

class MessageForm(BaseMessageForm):
    class Meta(BaseMessageForm.Meta):
        model = Message