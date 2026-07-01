from django import forms
from django.core.exceptions import ValidationError

from apps.chat.models import Conversation

class ConversationAdminForm(forms.ModelForm):
    class Meta:
        model = Conversation
        fields = "__all__"

    def clean_users(self):
        users = self.cleaned_data["users"]

        if users.count() != 2:
            raise ValidationError("A conversation must have exactly two users.")
        
        user1, user2 = users[0], users[1]

        if user1 == user2:
            raise ValidationError("A conversation must have two different users")

        return users
