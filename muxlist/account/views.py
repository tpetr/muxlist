from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from muxlist.account.forms import InviteRequestForm

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
