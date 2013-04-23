from django.views.generic import View
from django.shortcuts import render
from django.template import RequestContext

class search(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            # return user specific results
            return render(request, 'results.html', RequestContext(request))
        else:
            # Return some generic results
            return render(request, 'results.html', RequestContext(request))
