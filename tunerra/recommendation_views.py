from tunerra import models
from django.http import HttpResponse
from django.views.generic import View
import requests
import json
import urllib2
import time
from recommendations import recommendSong, recommendUser

lastFmLink_Track = 'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key=64e400a9de3b4287b61df31a91237cb3&artist=!&track=$&format=json'

class PersonRecommendation(View):
    def post(self, request, *args, **kwargs):
        recommended_user = recommendUser(request.user)

        return_dict = [{"usr_name": recommended_user.username, "usr_url": ("/accounts/profile/" + recommended_user.username)}]

        return_content = json.dumps(return_dict)
        print return_content
        response = HttpResponse(content=return_content, status=200)
        return response


class MusicRecommendation(View):
    def post(self, request, *args, **kwargs):
        # Just return 3 recommendations
        rec_songs = []
        for x in range(3):
            song = recommendSong(request.user)
            recommendation = models.MusicRecommendation(user=request.user, song=song)
            recommendation.save()
            cover_url = song.album.cover_art_url
            provider_url = get_provider_link(song)

            rec_songs.append({
                "cover_url": cover_url,
                "title": song.title,
                "artist": song.artist.name,
                "provider_url": provider_url
            })

        return HttpResponse(content=json.dumps(rec_songs), status=200)


def get_provider_link(song):
    provider_url = ""
    beatport_provider = models.MetadataProvider.objects.get(name='Beatport')
    if song.provider == beatport_provider:
        r = requests.get('http://api.beatport.com/catalog/3/beatport/track?id='+ str(song.provider_track_id))
        if r.status_code == 200:
            r_content = r.json()
            provider_url = 'http://beatport.com/track/' + r_content['results']['track']['slug'] + '/' + str(song.provider_track_id)
    else:
        url = lastFmLink_Track.replace('!', song.artist.name.replace(' ', '+')).replace('$', song.title.replace(' ', '+')).replace(' ', '')
        req = urllib2.Request(url)
        head = urllib2.build_opener()
        try:
            jsonSong = json.load(head.open(req))
            provider_url = jsonSong['track']['url']
        except:
            provider_url = ""

    return provider_url