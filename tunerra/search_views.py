from django.views.generic import View
from django.shortcuts import render
from django.template import RequestContext
from tunerra import recommendations
import random


class search(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():

            print "REQUEST IS: " + str(request)

            print "recommendations"
            # return user specific results
            newSong = recommendations.recommendSong(request.user)
            print newSong.title
            print newSong.artist.name

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
                songList.append(recommendations.recommendSong)

        numArtist = Artist.objcets.filter(name = text)
        if numArtist.count() > 0:
            currArtist = Artist.objects.get(name = text)
            artSongs = Songs.objects.filter(artist = currArtist)
            i = random.randInt(0, artSongs.count())
            for x in range(0, artSongs.count()):

                songList.append(artSongs[i])
            for x in range(0, artSongs.count()):
                if x > 3:
                    continue
                i = random.randInt(0, artSongs.count())
                songList.append(recommendations.recommendSong(user, artSongs[i].genre))

        numAlbum = Album.objects.filter(name = text)
        if numAlbum.count() > 0:
            currAlbum = Album.objects.get(name = text)
            currSongs = Songs.objects.get(album = currAlbum)
            for x in range(0, currSongs.count()):
                if x > 3:
                    continue
                i = random.randInt(0, currSongs.count())
                songList.append(currSongs[i])
                songList.append(recommendations.recommendSong(user,currSongs[i].genre))
        
        userList.append(recommendations.recommendUser(user))

        numPerson = User.objects.filter(name = text)
        if numPerson.count() > 0:
            











