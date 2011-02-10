from django import forms
from muxlist.account.models import InviteRequest, Invite
from django.contrib.auth.models import User
import hashlib
from django.core.mail import send_mail
from django.template.loader import render_to_string
from settings import HOSTNAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from boto.ses import SESConnection

attrs_dict = {'class': 'required'}

class InviteRequestForm(forms.ModelForm):
    class Meta:
        model = InviteRequest
        fields = ['email']

class SendInviteForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SendInviteForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        try:
            user = User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError('A user with that email address already exists')
    def clean(self):
        if self.user.get_profile().invites == 0:
            raise forms.ValidationError("You don't have any invites left")
        return self.cleaned_data

    def save(self):
        invite = super(SendInviteForm, self).save(commit=False)
        h = hashlib.md5("%s%sfunkyfresh" % (self.user.id, invite.email))
        invite.code = h.hexdigest()
        invite.owner = self.user
        invite.save()
        p = self.user.get_profile()
        p.invites -= 1
        p.save()
        c = SESConnection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        send_mail("[muxlist] You're invited!", render_to_string('email/invite.html', {'hostname': HOSTNAME, 'invite': invite}), 'trpetr@gmail.com', [invite.email])
        return invite

    class Meta:
        model = Invite
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

    def clean_email(self):
        try:
            user = User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError('A user with that email address already exists')

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
        

    
