from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from muxlist.account.forms import InviteRequestForm, InviteForm, SendInviteForm
from muxlist.account.models import Invite

def launch_page(request):
    if request.method == "POST":
        form = InviteRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = InviteRequestForm()

    return render_to_response('index.html', {'form': form})

def launch_page_thanks(request):
    form = InviteRequestForm()

    return render_to_response('thanks.html', {'form': form})

def okay(request):
    return render_to_response('okay.html', {})

def send_invite(request):
    if request.method == 'POST':
        form = SendInviteForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/mix/test/")
    else:
        form = SendInviteForm(request.user)
    return render_to_response('send_invite.html', {'form': form})

def invite(request, code):
    try:
        Invite.objects.get(code=code)
    except Invite.DoesNotExist: 
        raise Http404()
    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/okay/")
    else:
        form = InviteForm()
    return render_to_response('invite.html', {'form': form, 'code': code})
