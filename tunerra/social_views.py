from django.views.generic import View
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render

class facebook_connect(View):
    def post(self, request, *args, **kwargs):
        pass

def facebook_api(request):
    return render(request, 'channel.html', RequestContext(request))
