from tunerra.models import *
from tunerra.models import Album, Song, UserPreferences, UserPreferredGenre, Follows, Favorites, Artist
import random
import traceback
import urllib2
import json
from django.db.models import Max
from django.contrib.auth.models import User

lastFmLink_Track = 'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key=64e400a9de3b4287b61df31a91237cb3&artist=!&track=$&format=json'
lastFmLink_Album = 'http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key=64e400a9de3b4287b61df31a91237cb3&artist=!&album=$&format=json'
lastFMLink_Tag = 'http://ws.audioscrobbler.com/2.0/?method=tag.gettoptracks&tag=!&api_key=64e400a9de3b4287b61df31a91237cb3&limit=200&format=json'

high_pop_weight = 0.85
med_pop_weight = 0.5
low_pop_weight = 0.05

currPopularity = 0
currWeight = float()

def getTopTagTracks(genOfRec):
    global high_pop_weight
    global med_pop_weight
    global low_pop_weight

    global currPopularity
    global currWeight



    print "Getting a top track from LastFM"
    songList = []
    fmLink = lastFMLink_Tag.replace('!', genOfRec.name).replace(' ', '')
    req = urllib2.Request(fmLink)
    head = urllib2.build_opener()
    print fmLink
    try:
        jsonTag = json.load(head.open(req))
    except Exception as e: 
        print e
        return None
    tagInfo = jsonTag['toptracks']
    i = random.randint(0, 200)
    try:
        song = tagInfo['track'][i]
    except:
        song = tagInfo['track'][0]
    credentials = dict()
    trueTitle = song['name']
    trueArtist = song['artist']['name']

    if Song.objects.filter(title=trueTitle, artist__name = trueArtist).exists():
        return Song.objects.get(title = trueTitle, artist__name = trueArtist)


    Stitle = song['name'].replace(' ', '+')
    Sartist = song['artist']['name'].replace(' ', '+')

    newLink = lastFmLink_Track.replace('!', Sartist).replace('$', Stitle).replace(' ', '')
    req = urllib2.Request(newLink)
    head = urllib2.build_opener()
    jsonSong = json.load(head.open(req))

    trackInfo = jsonSong['track']

    addToDatabase(trackInfo, 0)
    try:
        thisSong = Song.objects.get(title=trueTitle, artist__name = trueArtist)
    except:
        return None
    return thisSong

'''Recommends a song based on user likes and preferences'''
def recommendSong(user):

    global high_pop_weight
    global med_pop_weight
    global low_pop_weight

    global currPopularity
    global currWeight





    print "recommending song!"

    '''Get genres'''
    preferredGenres = UserPreferredGenre.objects.filter(user = user).filter(weight__gt = 0.0)

    '''Get user preferences'''
    currPrefs = UserPreferences.objects.get(user = user)

    currPopularity = int(currPrefs.preferred_popularity)
    if currPopularity == 3:
        print "currpop is 3!"
        currWeight = high_pop_weight
    elif currPopularity == 2:
        currWeight = med_pop_weight
    else:
        currWeight = low_pop_weight

    print "currWeight is: " + str(currWeight)


    '''If the user has preferred genres, select one'''
    genOfRec = None
    fUser = None

    if preferredGenres.count() > 0:
        genOfRec = decideGenre(preferredGenres)
    else:
        genOfRec, fUser = getNewGenre(user)

    print "Genre of rec is: " + genOfRec.name
    
    '''Decide based on popularity whether to check the charts'''
    if (decideGetTop(currPrefs)):
        print "getting top track"
        return getTopTagTracks(genOfRec)

    print "not getting top track"


    '''Based on popularity, return a random song from the database with the genre'''
    if decideGetRandom():
        print "decided getting random"
        try:
            return random.choice(Song.objects.filter(genre = genOfRec))
        except: return recommendSong(user)

    '''Get a favorite song in your genre from a user that you follow'''
    if decideGetFollowed():
        print "decided getting followed"
        if fUser == None:
            currFollow = Follows.objects.filter(user = user)
            '''Get favorites of people you follow'''
            print "getting favorites songs of followed"
            for f in currFollow:
                print f.following.username
            followFavSongs = Favorites.objects.filter(user__in = [fUser.following for fUser in currFollow])
            if followFavSongs.count() > 0:
                '''Get favorites of people you follow with your genre'''
                print "Fiter the genres from the songs"
                favGenSongs = followFavSongs.filter(song_id__genre = genOfRec)
                if favGenSongs.count() > 0:
                    return random.choice(favGenSongs).song_id

    print "just getting random song:"
    try:
        return random.choice(Song.objects.filter(genre = genOfRec))
    except:
        return recommendSong(user)

'''If the user doesn't have any favorite songs or genres,
we look to see if anyone the user is following has favorite genres
otherwise, we just choose a random one'''
'''Returns a new genre and another user that it got it from, None otherwise'''
def getNewGenre(user):
    global high_pop_weight
    global med_pop_weight
    global low_pop_weight

    global currPopularity
    global currWeight

    favSongs = Favorites.objects.filter(user = user)

    if favSongs.count() > 0:
        return choice(favSongs).song_id.genre, None

    currFollows = Follows.objects.filter(user = user)
    genreList = list(Genre.objects.all())
    if currFollows.count() == 0:
        return random.choice(genreList), None
    followList = list(Follows.objects.all())
    
    '''If 10 randomly selected users don't have any fav genres, 
    just choose randomly'''
    for i in range(1, 10):
        followedUser = random.choice(followList).user
        currUserFavs = Favorites.objects.filter(user = followedUser)
        if currUserFavs.count() < 1:
            continue
        return choice(currUserFavs).song_id.genre, followedUser
    return random.choice(genreList), None

'''If the user has preferred genres, choose one of them '''
def decideGenre(preferredGenres):
    global high_pop_weight
    global med_pop_weight
    global low_pop_weight

    global currPopularity
    global currWeight

    '''Normalize scores based on a scale of 100'''
    maxValG = preferredGenres[0]
    for prefG in preferredGenres:
        if prefG.weight > maxValG.weight:
            maxValG = prefG
    for prefG in preferredGenres:
        prefG.weight = prefG.weight/(maxValG.weight / 100)

    '''Choose one genre randomly based on weights'''
    maxValG = -1
    bestGenre = None
    for prefG in preferredGenres:
        if prefG.weight * random.random() > maxValG:
            bestGenre = prefG.genre
            maxValG = prefG.weight * random.random()
    return bestGenre


'''Based on popularity level, decide whether to look to the charts
to get the recommended track'''
def decideGetTop(currPrefs):
    global high_pop_weight
    global med_pop_weight
    global low_pop_weight
    global currPopularity
    global currWeight

    randVal = random.random() +.3
    print "getting top rand val is: " + str(randVal)
    print "currWeight is: " + str(currWeight)
    print "truth value is: " + str(currWeight > randVal)
    return (currWeight > randVal)
    
'''Based on popularity level, decide whether to look to a random
song in the user's preferred genres for the recommended track'''
def decideGetRandom():
    global high_pop_weight
    global med_pop_weight
    global low_pop_weight
    global currPopularity
    global currWeight


    randVal = random.random()
    if currPopularity == 3:
        return False
    if currPopularity == 2:
        return med_pop_weight + .2 < randVal
    return low_pop_weight + .2 < randVal

def decideGetFollowed():
    global high_pop_weight
    global med_pop_weight
    global low_pop_weight
    global currPopularity
    global currWeight


    randVal = random.random()
    print "getFollowed rand val is: " + str(randVal)
    return currWeight > randVal

'''Gets your favorite genre out of your preferred genre (most weight)'''
def getMaxFavGenre(preferredGenres):
    global high_pop_weight
    global med_pop_weight
    global low_pop_weight
    global currPopularity
    global currWeight

    max_weight = preferredGenres.objects.all().aggregate(Max('weight'))['weight__max']
    return preferredGenres.objects.filter(weight =  max_weight)[0]

def recommendUser(user):
    global high_pop_weight
    global med_pop_weight
    global low_pop_weight
    global currPopularity
    global currWeight

    currPopularity = int(currPrefs.preferred_popularity)
    if currPopularity == 3:
        currWeight = high_pop_weight
    elif currPopularity == 2:
        currWeight = med_pop_weight
    else:
        currWeight = low_pop_weight

    '''Get people you follow'''
    youFollow = Follows.objects.filter(user = user)

    '''Get your fav genres'''
    favGenres = UserPreferredGenre.objects.filter(user = user)


    '''First search for people who also follow who you follow'''
    otherFollow = Follows.objects.select_related().filter(follows__in = [youFollow.following for fUser in  youFollow])


    if otherFollow.count() > 0:
        return recommendFollows(user, otherFollow)

    '''If there still isn't anybody, just find someone randomly who shares a genre with you'''
    for favGenre in random.shuffle(favGenres):
        targUsers = UserPreferredGenre.objects.select_related().filter(genre = favGenre).filter(weight__gt = 0.0)
        if targUsers.count() > 0:
            return random.shuffle(targUsers)[0].user

    '''If we still can't find anyone, just find someone randomly that has same popularity level'''
    simPopUsers = UserPreferences.objects.filter(preferred_popularity = currPopularity)
    if simPopUsers.count() > 0:
        return random.shuffle(simPopUsers)[0].user

    '''Default to a random user if we really can't find anyone'''
    while True:
        rIndex = random.randint(0, User.objects.all().count())
        try:
            return User.objects.all()[rIndex]
        except:
            pass

def recommendFollows(user, otherFollow):
    global high_pop_weight
    global med_pop_weight
    global low_pop_weight
    global currPopularity
    global currWeight


    '''Instead of just recommending anyone, try recommending someone that has the same favorite Genre as you'''    
    myFavGen = getMaxFavGenre(favGenres)
    for followEntry in random.shuffle(otherFollow):
        thisUser = followEntry.user
        if getMaxFavGenre(UserPreferredGenre.objects.filter(user = thisUser)) == myFavGen:
            return thisUser

    '''If that gets nobody, try recommending someone that has the same popularity level as you'''
    for followEntry in random.shuffle(otherFollow):
        thisUser = followEntry.user
        if thisUser.preferred_popularity == user.preferred_popularity:
            return thisUser

    '''Otherwise just get someone random'''
    return random.shuffle(otherFollow)[0].user





def addToDatabase(trackInfo, songsAdded):
#Otherwise let's insert it into the database
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
        songDict['bpm'] = 0
        songDict['length'] = 0
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
        if Album.objects.filter(name = albumDict['name']).exists():
            newAlb = Album.objects.get(name = albumDict['name'])
        else:
            newAlb, created = Album.objects.get_or_create(**albumDict)
        newGenre, created = Genre.objects.get_or_create(name = songDict['genre'])
        newArtist, created = Artist.objects.get_or_create(name = songDict['artist'])
        newProvider, created = MetadataProvider.objects.get_or_create(name = songDict['provider'])
        songDict['genre'] = newGenre
        songDict['artist'] = newArtist
        songDict['album'] = newAlb
        songDict['provider'] = newProvider
        Song.objects.get_or_create(**songDict)
        print "Added song " + trackInfo['name'] + ' - ' + trackInfo['artist']['name'] + ' to database'
        return songsAdded + 1
    except Exception as e:
        print e
        print traceback.print_exc()
        print "Error adding song!" 
        return songsAdded