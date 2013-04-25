from django.shortcuts import render
from django.views.generic import View
from django.template import RequestContext
from django.http import Http404, HttpResponseBadRequest, HttpResponse, HttpResponseForbidden
from tunerra import models, views
from datetime import datetime


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

        # Fetch all of this user's posts by creation time
        user_posts = models.Post.objects.filter(user=profile_user).order_by('-creation_time')[:10]

        favList = models.Favorites.objects.filter(user=request.user).order_by('-play_count')[:10]
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
            follow_object, created_now = models.Follows.objects.get_or_create(user=request.user, following=user_to_follow)
            response = HttpResponse()
            response.status_code = 200
            # The content is equal to what the UI state should be AFTER this request
            if not created_now:
                # unfollow
                follow_object.delete()
                response.content = "Follow"
            else:
                # follow
                response.content = "Unfollow"
            return response
        else:
            return HttpResponseBadRequest


class ProfilePostLike(View):
    def post(self, request, *args, **kwargs):
        try:
            like_username = request.POST['like_username']
            user_record = models.User.objects.get(username=like_username)
            post_id = int(request.POST['post_id'])
            post_record = models.Post.objects.get(pk=post_id)
            like_record, created = models.Like.objects.get_or_create(user=user_record, liked_post=post_record)
            response = HttpResponse()
            response.status_code = 200
            if not created:
                response.content = "unliked"
                like_record.delete()
            else:
                response.content = "liked"
            return response
        except:
            return HttpResponseBadRequest()