from django import forms
from muxlist.account.models import InviteRequest

class InviteRequestForm(forms.ModelForm):
    class Meta:
        model = InviteRequest
        fields = ['email']
