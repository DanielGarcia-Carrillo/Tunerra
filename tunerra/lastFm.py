from tunerra.models import Song, Album, Artist, Genre, MetadataProvider, Favorites
import urllib2
import json
import datetime


lastFmLink_Album = 'http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key=64e400a9de3b4287b61df31a91237cb3&artist=!&album=$&format=json'
lastFmLink_Track = 'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key=64e400a9de3b4287b61df31a91237cb3&artist=!&track=$&format=json'

'''Validates and enters new song into database'''
def getLastFmSong(title, artist):
    print "getting last FM song"
    mtitle = title.replace(' ', '+')
    martist = artist.replace(' ', '+')
    newLink = lastFmLink_Track.replace('!', martist).replace('$', mtitle).replace(' ', '')
    req = urllib2.Request(newLink)
    head = urllib2.build_opener()
    try:
        jsonSong = json.load(head.open(req))        
    except: return None
    if 'error' in jsonSong:
        print "error in json song"
        return None
    trackInfo = jsonSong['track']
    try:
        thisSong = Song.objects.get(title = title, artist__name = artist)
        print "Song found already!"
        return thisSong
    except:
        pass
    print "about to add to database"
    return addToDatabase(trackInfo, 0)


def getLastFMSongAuth(title, artist, user):
    newSong = getLastFmSong(title, artist)
    print "New song name is: " + newSong.title
    try:
        print "Adding the favorite for " + str(user)
        print "Song is " + newSong.title + " - " + newSong.artist.name
        thisFav = Favorites(user = user, song_id = newSong, last_played = datetime.datetime.now().strftime("%Y-%m-%d"))
        print str(thisFav)
        thisFav.save()
    except Exception as e:
            pass




def addToDatabase(trackInfo, songsAdded):
#Otherwise let's insert it into the database
    print "Adding song into database"
    try:
        songDict = dict()
        albumDict = dict()
        songDict['title'] = trackInfo['name']
        print songDict['title']
        songDict['artist'] = trackInfo['artist']['name']
        print songDict['artist']
        try:
            songDict['genre'] = trackInfo['toptags']['tag'][0]['name']
        except:
            songDict['genre'] = 'default'
        songDict['album'] = trackInfo['album']['title']
        albumDict['name'] = trackInfo['album']['title']
        try:
            songDict['track_number'] = trackInfo['album']['@attr']['position']
        except:
            songDict['track_number'] = 0
        songDict['provider'] = 'Last_FM'
        songDict['provider_track_id'] = trackInfo['id']
        newLink = lastFmLink_Album.replace('!', songDict['artist'].replace(' ', '+')).replace('$', songDict['album'].replace(' ', '+'))
        req = urllib2.Request(newLink)
        head = urllib2.build_opener()
        jsonAlbum = json.load(head.open(req))['album']
        try:
            albumDict['year']= jsonAlbum['releasedate'].strip()
            albumDict['year'] = datetime.datetime.strptime(albumDict['year'], '%d %b %Y, %H:%M').strftime('%Y-%m-%d')
        except:
            print "Default date"
            albumDict['year'] = '1900-01-01'
        popularity = 0.0
        image_url = ''
        try:
            for imageFile in jsonAlbum['image']:
                if imageFile['size'] == 'mega':
                    albumDict['cover_art_url'] = imageFile['#text']
        except:
            print "Default cover"
            albumDict['cover_art_url'] = ''
        print "Saving stuff"
        newAlb, created = Album.objects.get_or_create(**albumDict)
        newGenre, created = Genre.objects.get_or_create(name = songDict['genre'])
        newArtist, created = Artist.objects.get_or_create(name = songDict['artist'])
        newProvider, created = MetadataProvider.objects.get_or_create(name = songDict['provider'])
        songDict['genre'] = newGenre
        songDict['artist'] = newArtist
        songDict['album'] = newAlb
        songDict['provider'] = newProvider
        newSong = Song(**songDict)
        newSong.save()
        return newSong
    except Exception as e:
        print e
        return None
