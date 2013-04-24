import tunerra.models
import random
import urllib2
import tunerra.importServer
from django.db.models import Max

lastFmLink_Track = 'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key=64e400a9de3b4287b61df31a91237cb3&artist=!&track=$&format=json'
lastFmLink_Album = 'http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key=64e400a9de3b4287b61df31a91237cb3&artist=!&album=$&format=json'
lastFMLink_Tag = "http://ws.audioscrobbler.com/2.0/?method=tag.gettoptracks&tag=!&api_key=64e400a9de3b4287b61df31a91237cb3&limit=100&format=json"

high_pop_weight = 0.85
med_pop_weight = 0.5
low_pop_weight = 0.05

currPopularity = 0
currWeight = 0

def getTopTagTracks(genOfRec):
    songList = []
    fmLink = lastFMLink_Tag.replace('!', genOfRec.name)
    req = urllib2.Request(fmLink)
    head = urllib2.build_opener()
    try:
        jsonTag = json.load(head.open(req))
    except: return None
    tagInfo = jsonTag['toptracks']
    i = random(0, len(tagInfo))
    song = tagInfo[i]
    credentials = dict()
    Stitle = song['name']
    Sartist = song['artist']['name']

    newLink = lastFmLink_Track.replace('!', artist).replace('$', name).replace(' ', '')
    req = urllib2.Request(newLink)
    head = urllib2.build_opener()
    jsonSong = json.load(head.open(req))

    trackInfo = jsonSong['track']

    addToDatabase(trackInfo, 0)
    return Song.objects.get(title=Stitle, artist = Sartist)

'''Recommends a song based on user likes and preferences'''
def recommendSong(user):

    '''Get genres'''
    preferredGenres = UserPreferredGenre.objects.filter(user = user).filter(weight > 0.0)

    '''Get user preferences'''
    currPrefs = UserPreferences.objects.filter(user = user)

    currPopularity = int(currPrefs.preferred_popularity)
    if currPopularity == 3:
        currWeight = high_pop_weight
    elif currPopularity == 2:
        currWeight = med_pop_weight
    else:
        currWeight = low_pop_weight


    '''If the user has preferred genres, select one'''
    genOfRec = None
    fUser = None

    if preferredGenres.count() > 0:
        genOfRec = decideGenre(preferredGenres)
    else:
        genOfRec, fUser = getNewGenre(user)
    
    '''Decide based on popularity whether to check the charts'''
    if (decideGetTop(currPrefs)):
        return getTopTagTracks(genOfRec)


    '''Based on popularity, return a random song from the database with the genre'''
    if decideGetRandom():
        return random.choice(Song.objects.filter(genre = genOfRec))

    '''Get a favorite song in your genre from a user that you follow'''
    if decideGetFollowed():
        if fUser == None:
            currFollow = Follows.objects.filter(user = user)
            '''Get favorites of people you follow'''
            followFavSongs = Favorites.objects.filter(user__in = [fUser.following for fUser in currFollow])
            if followFavSongs.count() > 1:
                '''Get favorites of people you follow with your genre'''
                favGenSongs = followFavSongs.filter(song_id__genre__exact = genOfRec)
                if favGenSongs.count() > 1:
                    return random.choice(favGenSongs).song_id

    return random.choice(Song.objects.filter(genre = genOfRec))

'''If the user doesn't have any favorite songs or genres,
we look to see if anyone the user is following has favorite genres
otherwise, we just choose a random one'''
'''Returns a new genre and another user that it got it from, None otherwise'''
def getNewGenre(user):

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
    randVal = random.random()
    return currWeight > randVal
    
'''Based on popularity level, decide whether to look to a random
song in the user's preferred genres for the recommended track'''
def decideGetRandom():
    randVal = random.random()
    if currPopularity == 3:
        return False
    if currPopularity == 2:
        return med_pop_weight + .2 < randVal
    return low_pop_weight + .2 < randVal

def decideGetFollowed():
    randVal = random.random()
    return currWeight > randVal

'''Gets your favorite genre out of your preferred genre (most weight)'''
def getMaxFavGenre(preferredGenres):
    max_weight = preferredGenres.objects.all().aggregate(Max('weight'))['weight__max']
    return preferredGenres.objects.filter(weight =  max_weight)[0]

def recommendUser(user):
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
        targUsers = UserPreferredGenre.objects.select_related().filter(genre = favGenre).filter(weight > 0,0)
        if targUsers.count() > 0:
            return random.shuffle(targUsers)[0].user

    '''If we still can't find anyone, just find someone randomly that has same popularity level'''
    simPopUsers = UserPreferences.objects.filter(preferred_popularity = currPopularity)
    if simPopUsers.count() > 0:
        return random.shuffle(simPopUsers)[0].user

    '''Default to a random user if we really can't find anyone'''
    while True:
        rIndex = random.random(0, User.objects.all().count())
        try:
            return User.objects.all()[rIndex]
        except:
            pass

def recommendFollows(user, otherFollow):
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
