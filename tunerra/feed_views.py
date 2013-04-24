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
        # TODO get all posts that are music recommendations, follow recommendations and
        # Order posts by descending creation_time order and get 10 latest TODO respond to pagination, ie get later pages on request
        music_recs = models.MusicRecommendation.objects.filter(user=request.user).order_by('-creation_time')[:10]
        follow_recs = models.FollowRecommendation.objects.filter(user=request.user).order_by('-creation_time')[:10]
        follows = models.Follows.objects.filter(user=request.user)
        # essentially an inner join: user__in
        feed_posts = models.Post.objects.filter(user__in=[f.following for f in follows]).order_by('-creation_time')[:10]

        return {'feed_posts': feed_posts, 'music_recs': music_recs, 'follow_recs': follow_recs}


class PostForm(forms.Form):
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'title', 'required': True, 'class':'input-block-level'}))
    artist = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'artist', 'required': True, 'class':'input-block-level'}))
    body = forms.CharField(max_length=1500, widget=forms.Textarea(attrs={'rows': '2'}), required=False)
