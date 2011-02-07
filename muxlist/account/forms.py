from django import forms
from muxlist.account.models import InviteRequest, Invite
from django.contrib.auth.models import User

attrs_dict = {'class': 'required'}

class InviteRequestForm(forms.ModelForm):
    class Meta:
        model = InviteRequest
        fields = ['email']

class InviteForm(forms.Form):
    invite_code = forms.CharField(max_length=32, widget=forms.HiddenInput())
    username = forms.RegexField(regex=r'^\w+$', max_length=30)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False), label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False), label="Password (again)")

    def clean_username(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError("A user with that username already exists")

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("Your passwords didnt match")
        try: 
            Invite.objects.get(code=self.cleaned_data['invite_code'])
        except Invite.DoesNotExist:
            raise forms.ValidationError('Invalid invite code')
        return self.cleaned_data

    def save(self):
        invite = Invite.objects.get(code=self.cleaned_data['invite_code'])
        user = User.objects.create_user(self.cleaned_data['username'], invite.email, self.cleaned_data['password1'])
        profile = user.get_profile()
        profile.parent = invite.owner.get_profile()
        profile.save()
        invite.delete()
        return user
        

    
