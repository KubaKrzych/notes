from django import forms
from .models import Note


class NoteForm(forms.ModelForm):
    encryption_key = forms.CharField(required=False, widget=forms.PasswordInput())
    shared_with_users = forms.CharField(required=False)

    class Meta:
        model = Note
        fields = ["title", "content", "encryption_status", "sharing_status"]

    def clean_shared_with_users(self):
        usernames = self.cleaned_data.get("shared_with_users", "")
        return [name.strip() for name in usernames.split(",") if name.strip()]
