from django.views.generic import View
from django.shortcuts import render
from django.template import RequestContext
from tunerra import recommendations

class search(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            print "recommendations"
            # return user specific results
            newSong = recommendations.recommendSong(request.user)
            print newSong.title
            print newSong.artist.name

            return render(request, 'results.html', RequestContext(request))
        else:
            # Return some generic results
            return render(request, 'results.html', RequestContext(request))
