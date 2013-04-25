from django.views.generic import View
from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth import logout
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from tunerra import models
from django import forms
from lastFm import getLastFmSong


class FeedPage(View):
    # POSTing to the page is literally for making posts on a profile
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            form = PostForm(request.POST)
            if form.is_valid():
                artist_name = form.cleaned_data['artist']
                song_title = form.cleaned_data['title']

                try:
                    artist_record = models.Artist.objects.get(name=artist_name)
                    song_record = models.Song.objects.get(title=song_title, artist=artist_record)
                except:
                    song_record = getLastFmSong(song_title, artist_name)

                song_errors = list()
                if song_record:
                    saved_post = models.Post(body=form.cleaned_data['body'], song=song_record, user=models.User.objects.get(username=request.user.username))
                    saved_post.save()
                else:
                    song_errors.append('Given song doesn\'t exist in our records')

                profile_context = self.page_context(request)
                profile_context.update({'post_form': PostForm()})
                profile_context.update({'song_errors': song_errors})
                return render(request, 'feed.html', RequestContext(request, profile_context))
            else:
                f
                profile_context = self.page_context(request)
                profile_context.update({'post_form': form})
                return render(request, 'feed.html', RequestContext(request, profile_context))
        else:
            return HttpResponseForbidden()

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
        # Order posts by descending creation_time order and get 10 latest TODO respond to pagination, ie get later pages on request
        music_recs = models.MusicRecommendation.objects.filter(user=request.user).order_by('-creation_time')[:10]
        follow_recs = models.FollowRecommendation.objects.filter(user=request.user).order_by('-creation_time')[:10]
        follows = models.Follows.objects.filter(user=request.user)
        self_and_following = [f.following for f in follows]
        self_and_following.append(models.User.objects.get(username=request.user.username))
        # essentially an inner join: user__in
        feed_posts = models.Post.objects.filter(user__in=self_and_following).order_by('-creation_time')[:10]

        return {'feed_posts': feed_posts, 'music_recs': music_recs, 'follow_recs': follow_recs}


class PostForm(forms.Form):
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'title', 'required': True, 'class':'input-block-level'}))
    artist = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'artist', 'required': True, 'class':'input-block-level'}))
    body = forms.CharField(max_length=1500, widget=forms.Textarea(attrs={'rows': '2'}), required=False)
