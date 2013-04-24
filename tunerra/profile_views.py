from django.shortcuts import render
from django.views.generic import View
from django.template import RequestContext
from django.http import Http404
from tunerra import models, views
from dajax.core import Dajax


class ProfilePage(View):
    def get(self, request, *args, **kwargs):
        # Check if current user is following this person
        following = False
        same_user = False
        try:
            profile_user = models.User.objects.get(username=kwargs['username'])
        except:
            raise Http404
        if request.user.is_authenticated():
            same_user = profile_user.username == request.user.username
            if models.Follows.objects.filter(user=request.user, following=profile_user):
                following = True

        # Fetch all of this users posts by creation time
        user_posts = models.Post.objects.filter(user=profile_user).order_by('-creation_time')[:10]

        # SELECT FROM Favorites WHERE user = ?
        favList = models.Favorites.objects.filter(user=request.user)
        favSongList = list()
        for fav in favList:
            currSong = fav.song_id
            # print currSong.title
            favSongList.append(currSong)

        #TODO make sure liking ability is locked if the current user already liked the post
        return render(request, 'profile.html', RequestContext(request, {'following': following,
                                                                        'same_user': same_user,
                                                                        'profile_posts': user_posts,
                                                                        'FavList': favSongList}))


class ProfileFollow(View):
    def get(self, request, *args, **kwargs):
        try:
            user_to_follow = models.User.objects.get(username=kwargs['username'])
        except:
            raise Http404
        if request.user.is_authenticated() and not user_to_follow == request.user:
            follow_object, created = models.Follows.objects.get_or_create(user=request.user, following=user_to_follow)
            if created:
                # throw some error, the follow was already created
                raise Http404
            return # SOME sort of response to jquery to tell it that you are now following
        else:
            raise Http404


class ProfileUnfollow(View):
    def get(self, request, *args, **kwargs):
        try:
            user_to_unfollow = models.User.objects.get(username=kwargs['username'])
        except:
            raise Http404
        if request.user.is_authenticated():
            try:
                models.Follows.objects.get(user=request.user, following=user_to_unfollow).delete()
            except:
                raise Http404
            return # give a response indicating that you are no longer following this person
        else:
            raise Http404


class ProfilePostLike(View):
    def get(self, request, *args, **kwargs):
        return views.index(request)