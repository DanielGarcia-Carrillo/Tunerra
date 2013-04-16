from django.views.generic import View
from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth import logout
from django.http import Http404
from tunerra import models
from django import forms

class ProfilePage(View):
    # POSTing to the profile page is literally for making posts on a profile
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            form = PostForm(request.POST)
            if form.is_valid():
                saved_post = models.Post(user=request.user, body=form.cleaned_data['body'], likes=0)
                saved_post.save()
                return render(request, 'profile.html', RequestContext(request, {'post_form': PostForm()}))
            else:
                return render(request, 'profile.html', RequestContext(request, {'post_form': form}))
        else:
            # TODO throw some error or something
            pass

    # GETting the profile page just displays it
    def get(self, request, *args, **kwargs):
        if (request.user.is_authenticated() and request.user.username == kwargs['username']):
            # SELECT FROM Favorites WHERE user = ?
            favList = models.Favorites.objects.filter(user=request.user)
            favSongList = list()
            for fav in favList:
                currSong = fav.song_id
                # print currSong.title
                favSongList.append(currSong)
            return render(request, 'profile.html', {'FavList': favSongList, 'post_form': PostForm()})
        else:
            logout(request)
            raise Http404

class PostForm(forms.Form):
    body = forms.CharField(max_length=1500, widget=forms.Textarea(attrs={'placeholder':'What are you listening to right now?', 'rows':'2'}))