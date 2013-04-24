from django.shortcuts import render
from django.views.generic import View
from django.template import RequestContext
from tunerra import models


class ProfilePage(View):
    def get(self, request, *args, **kwargs):
        # Check if current user is following this person
        following = False
        if request.user.is_authenticated():
            profile_user = models.User.objects.get(username=kwargs['username'])
            if models.Follows.objects.get(user=request.user, following=profile_user):
                following = True

        # Fetch all of this users posts by creation time
        profile_user = models.User.objects.get(username=kwargs['username'])
        user_posts = models.Post.objects.filter(user=profile_user).order_by('-creation_time')[:10]

        return render(request, 'profile.html', RequestContext(request, {'following': following,
                                                                        'profile_posts': user_posts}))


class ProfileFollow(View):
    def get(self, request, *args, **kwargs):
        user_to_follow = kwargs['username']
        return # SOME sort of response to jquery to tell it that you are now following


class ProfileUnfollow(View):
    def get(self, request, *args, **kwargs):
        user_to_unfollow = kwargs['username']
        return # give a response indicating that you are no longer following this person