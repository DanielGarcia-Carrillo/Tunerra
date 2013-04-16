from django.views.generic import View
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpRequest

class search(View):
    def get(self, request, *args, **kwargs):
        request = HttpRequest(request)
        if request.user.is_authenticated():
            # return user specific results
            pass
        else:
            # Return some generic results
            return render(request, 'results.html', RequestContext(request))
