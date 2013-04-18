from django.views.generic import View
from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth import logout
from django.http import Http404, HttpResponseRedirect
from tunerra import models
from django import forms


class FeedPage(View):
    # POSTing to the profile page is literally for making posts on a profile
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            form = PostForm(request.POST)
            if form.is_valid():
                saved_post = models.Post(user=request.user, body=form.cleaned_data['body'], likes=0, type='U')
                saved_post.save()
                profile_context = self.page_context(request)
                profile_context.update({'post_form': PostForm()})
                return render(request, 'feed.html', RequestContext(request, profile_context))
            else:
                profile_context = self.page_context(request)
                profile_context.update({'post_form': form})
                return render(request, 'feed.html', RequestContext(request, profile_context))
        else:
            # TODO throw some error or something
            pass

    # GETting the profile page just displays it
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.username == kwargs['username']:
            profile_context = self.page_context(request)
            profile_context.update({'post_form': PostForm()})
            return render(request, 'feed.html', RequestContext(request, profile_context))
        else:
            logout(request)
            raise Http404

    def page_context(self, request):
        # SELECT FROM Favorites WHERE user = ?
        favList = models.Favorites.objects.filter(user=request.user)
        favSongList = list()
        for fav in favList:
            currSong = fav.song_id
            # print currSong.title
            favSongList.append(currSong)

        # Order posts by descending creation_time order and get 10 latest TODO respond to pagination, ie get later pages on request
        posts = models.Post.objects.filter(user=request.user).order_by('-creation_time')[:10]
        profile_posts = list()
        for p in posts:
            post_dict = {'body': p.body,
                         'likes': p.likes,
                         'time': p.creation_time,
                         'type': p.type,
                         'recommendation': p.follow_rec if p.follow_rec else p.song
            }
            profile_posts.append(post_dict)

        return {'FavList': favSongList, 'profile_posts': profile_posts}


class PostForm(forms.Form):
    artist = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'artist'}))
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'title'}))