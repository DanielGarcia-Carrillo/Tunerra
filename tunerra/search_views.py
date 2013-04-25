from tunerra.models import *
from tunerra.models import Album, Song, UserPreferences, UserPreferredGenre, Follows, Favorites, Artist
from django.views.generic import View
from django.shortcuts import render
from django.template import RequestContext
from tunerra import recommendations
import random


class search(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():

            print "recommendations"
            # return user specific results
            songList, userList = self.parseText(request.user, request.POST['query'])
            print songList
            print userList

            return render(request, 'results.html', RequestContext(request))
        else:

            # Return some generic results
            return render(request, 'results.html', RequestContext(request))

    '''Find out if this is a song, person, artist, genre'''
    def parseText(self, user, text):

        text = text.strip()

        songList = list()
        userList = list()

        numSongs = Song.objects.filter(title = text).count()
        if numSongs > 0:
            for x in range(0, numSongs):
                if x > 3:
                    recommendations.recommendSong(user, Song.genre)
                songList.append(Song.objects.filter(title = text)[x])

        numGenre = Genre.objects.filter(name = text)
        if numGenre.count() > 0:
            currGenre = Genre.objects.get(name = text)
            for x in range (0, 3):
                songList.append(recommendations.recommendSong(user, currGenre))

        numArtist = Artist.objects.filter(name = text)
        if numArtist.count() > 0:
            currArtist = Artist.objects.get(name = text)
            artSongs = Song.objects.filter(artist = currArtist)
            i = random.randint(0, artSongs.count())
            for x in range(0, artSongs.count()):
                if x > 3:
                    continue
                songList.append(artSongs[x])
            for x in range(0, artSongs.count()):
                if x > 7:
                    continue
                i = random.randint(0, artSongs.count())
                try:
                    songList.append(recommendations.recommendSong(user, artSongs[i].genre))
                except:
                    continue

        numAlbum = Album.objects.filter(name = text)
        if numAlbum.count() > 0:
            currAlbum = Album.objects.get(name = text)
            currSongs = Songs.objects.get(album = currAlbum)
            for x in range(0, currSongs.count()):
                if x > 3:
                    continue
                i = random.randint(0, currSongs.count())
                songList.append(currSongs[i])
                songList.append(recommendations.recommendSong(user,currSongs[i].genre))
        
        userList.append(recommendations.recommendUser(user))

        numPerson = User.objects.filter(username = text)
        if numPerson.count() > 0:
            currUser = numPerson[0]
            for x in range(0, 3):
                userList.append(recommendations.recommendUser(currUser))
                songList.append(recommendations.recommendSong(currUser))
            followSet = Follows.objects.filter(user = currUser)
            for use in followSet:
                userList.append(use.user)
                userList.append(use.following)
                random.shuffle(userList)
            userList.append(numPerson[0])
        random.shuffle(songList)
        random.shuffle(userList)

        return list(set(songList)), list(set(userList))













