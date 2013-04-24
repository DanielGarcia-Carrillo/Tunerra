from django.template import RequestContext
from django.shortcuts import render
from django import forms
from tunerra.models import Song, Favorites, UserPreferences, Region, UserPreferredGenre, Genre
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import urllib
import json
import sys
from xml.dom import minidom
from urllib import urlopen

last_fm_key = '61994d32a190d0a98684e84d6f38b41a'
fm_loved_str = 'http://ws.audioscrobbler.com/2.0/?method=user.getlovedtracks&user='
POPULARITY_CHOICE = {('1', 'Low Popularity'),
 ('2', 'Normal Popularity'), ('3', 'High Popularity')}



#Add songs
def parse_LastFM_love(xmltree, request):
    for lfm in xmltree.getElementsByTagName('lfm'):
        for lovedSongs in xmltree.getElementsByTagName('lovedtracks'):
            for song in lfm.getElementsByTagName('track'):
                try:
                    title = song.getElementsByTagName('name')[0].firstChild.nodeValue
                    artist = song.getElementsByTagName('artist')[0].getElementsByTagName('name')[0].firstChild.nodeValue
                    newSong = Song(title = title, artist = artist, album='noalb', year ='1999-01-22')
                except: continue

                newSong.save()
                newFav = Favorites()
                user = request.user
                hotness_level = 0
                song_id = newSong
                play_count = 1
                last_played = song.getElementsByTagName('date')[0].firstChild.nodeValue

                newFav = Favorites(user = user, hotness_level = hotness_level, song_id = song_id, play_count = play_count, last_played='1999-01-22')
                newFav.save()

                # print "SONGS ARE: " + song.getElementsByTagName('name')[0].firstChild.nodeValue


def index(request):
    if request.user.is_authenticated():
        return render(request, 'map.html', RequestContext(request))
        #return HttpResponseRedirect('/accounts/profile/'+request.user.username)
    else:
        # Treat them as anonymous user
        return render(request, 'index.html', RequestContext(request))
    
def map_page(request):
    currPrefs = UserPreferences.objects.filter(user = request.user)
    if not currPrefs:
        return render(request, 'map.html', None)
    else:
        currPrefs = currPrefs[0]
        currRegion = currPrefs.preferred_region
        return render(request, 'map.html', {'username': request.user.username, 'lat': currRegion.lat, 'lng': currRegion.lng})

def login_error(request):
    return render(request, 'login_error.html', RequestContext(request))

def settingsPage(request, pagename, vals):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login_error')
    if request.method == 'GET':
        if vals:
            prefForm = prefsForm(initial=vals)
        else:
            prefForm = prefsForm(request.GET)
        favGenres = UserPreferredGenre.objects.filter(user = request.user)
        for favObj in favGenres:
            favObj.weight = favObj.weight * 11.0
        return render(request, pagename, {'prefsForm': prefForm, 'favGenres': favGenres} )
    
    #Request is a POST
    if 'confirmed-delete' in request.POST:
        #TODO make sure admins can't be deleted
        #DELETE FROM Users WHERE id = request.user.id
        request.user.delete()   #CASCADEs
        return HttpResponseRedirect('/')

    prefForm = prefsForm(request.POST)
    if prefForm.is_valid():
        lastFMusername = prefForm.cleaned_data['LastFMusername']
        fm_str_req = fm_loved_str + lastFMusername + "&api_key=" + last_fm_key
        parse_LastFM_love(minidom.parse(urllib.urlopen(fm_str_req)), request) 
        notify_val = prefForm.cleaned_data['notify_system']
        region_val = prefForm.cleaned_data['region']
        
        newReg = newRegion(region_val)
        
        #newReg = Region(region_val)
        newReg.save()

        pop_val = prefForm.cleaned_data['popularity']
        genre_val = prefForm.cleaned_data['genre']
        # SELECT FROM UserPreferences WHERE user=?, request.user
        user_pref = UserPreferences.objects.filter(user=request.user)
        if len(user_pref) != 0:
            user_pref = user_pref[0]
        if user_pref:
            # Update existing preferences
            user_pref.notify_system = notify_val
            user_pref.preferred_region = newReg
            user_pref.preferred_popularity = pop_val
            genreVals = genre_val.replace(' ', '_').split(',')
            myGenres = UserPreferredGenre.objects.filter(user = request.user)

            for favgen in myGenres:
                currGenreName = favgen.genre.name
                favgen.weight = float(request.POST[currGenreName])/11.0
                favgen.save(force_update= True)

            for genreWord in genreVals:
                currGenre, created = Genre.objects.get_or_create(name= genreWord)
                if not UserPreferredGenre.objects.filter(user=request.user, genre = currGenre).exists():
                    UserPreferredGenre.objects.get_or_create(user = request.user, genre = currGenre, weight=1.0)
            # UPDATE UserPreferences SET notify_system=?, preferred_region=?, preferred_popularity=?, preferred_genre=?, WHERE user=?
            user_pref.save()
        else:
            # Create new userprefs
            # INSERT INTO UserPreferences (user, notify_system, preferred_region, preferred_popularity, preferred_genre) VALUES ?,?,?,?,?
            newPrefs = UserPreferences(user = request.user, notify_system = notify_val,
            preferred_region = newReg, preferred_popularity = pop_val, last_fmName = lastFMusername)
            genreVals = genre_val.replace(' ', '_').split(',')
            for genreWord in genreVals:
                currGenre, created = Genre.objects.get_or_create(name= genreWord)
                UserPreferredGenre.objects.get_or_create(user = request.user, genre = currGenre, weight=1.0)

            newPrefs.save()
        return HttpResponseRedirect('/accounts/feed/'+request.user.username)
    else:
        favGenres = UserPreferredGenre.objects.filter(user = request.user)
        return render(request, pagename, {'prefsForm': prefForm, 'favGenres': favGenres} )

def welcome(request):
    return settingsPage(request, 'welcome.html', None)

def settings(request):
    # SELECT FROM UserPreferences WHERE user = ?
    currPrefs = UserPreferences.objects.filter(user = request.user)
    if not currPrefs:
        return settingsPage(request, 'settings.html', None)
    currPrefs = currPrefs[0]
    currNotify = currPrefs.notify_system
    currReg = currPrefs.preferred_region.name
    #currGenre = currPrefs.preferred_genre TODO fix genres for settings page
    currPop = currPrefs.preferred_popularity
    lastFM_username = currPrefs.last_fmName
    favGenreString= ""
    favGenres = UserPreferredGenre.objects.filter(user = request.user)
    for genreRow in favGenres:
        favGenreString = favGenreString + genreRow.genre.name +","
    favGenreString = favGenreString[:-1]

    vals = {'notify_system': currNotify, 'region': currReg, 
    'popularity': currPop, 'LastFMusername': lastFM_username, 'genre': favGenreString }

    return settingsPage(request, 'settings.html', vals)

def logout_user(request):
    # Logs out user through auth system
    logout(request)
    return HttpResponseRedirect('/')

def login_signup(request):
    if request.method == 'POST':
        if request.POST.get('form-name') == 'signup':
            signup_form = SignupForm(request.POST)
            if signup_form.is_valid():
                # SELECT * FROM SiteUser WHERE username = ?:  signup_form.cleaned_data['username']
                existing_user = User.objects.filter(username=signup_form.cleaned_data['username'])
                if not existing_user:
                    # INSERT INTO User (username, email, password) VALUES (?,?,?): username, email, password
                    new_user = User.objects.create_user(
                        username=signup_form.cleaned_data['username'],
                        email=signup_form.cleaned_data['email'],
                        password=signup_form.cleaned_data['password']
                    )
                    
                    
                    new_user2 = authenticate(username=signup_form.cleaned_data['username'], password=signup_form.cleaned_data['password'])
                    login(request, new_user2)
                    return HttpResponseRedirect('/accounts/welcome')
            # Returns current signup_form as env variable so that form errors will show up to user
            return render(request, 'accounts.html', {
                'signup_form':signup_form,
                'login_form':LoginForm()
            })
        elif request.POST.get('form-name') == 'login':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                login_username = login_form.cleaned_data['username']
                user = authenticate(username=login_username, password=login_form.cleaned_data['password'])
                if user is None:
                    # Return error that something is wrong
                    return HttpResponse()
                else:
                    login(request, user)
                    # Send to profile
                    return HttpResponseRedirect('/accounts/feed/'+login_username)
            else:
                # Returns current login_form so that the login form errors will show up to user
                return render(request, 'accounts.html', {
                    'signup_form':SignupForm(),
                    'login_form':login_form
                })
    else:
        return render(request, 'accounts.html', {
            'signup_form': SignupForm(),
            'login_form': LoginForm()
        })
        
#creates a new region object with latitude and longitude
def newRegion(region_val):                
    startURL = 'http://maps.google.com/maps/api/geocode/json?address='
    endURL = '&sensor=false'
    URL = startURL + region_val + endURL
                    
    data = json.load(urllib.urlopen(URL))
    if (data['status'] == "OK"):
        currReg = region_val
        rlat = data['results'][0]['geometry']['location']['lat']
        rlng = data['results'][0]['geometry']['location']['lng']
    else:
        currReg = "Champaign, IL"
        rlat = 42.0
        rlng = -88.0
    region, created = Region.objects.get_or_create(name=currReg, lat=rlat, lng=rlng)
    return region
        

class prefsForm(forms.Form):
    correct_size_text_input = widget=forms.TextInput(attrs={'class':'input-block-level'})
    notify_system = forms.BooleanField(required=False)
    region = forms.CharField(max_length=100, initial = 'Chicago', widget=correct_size_text_input)
    popularity = forms.ChoiceField(choices=POPULARITY_CHOICE, widget=forms.Select(attrs={'class':'input-block-level'}))
    genre = forms.CharField(max_length=100, widget=correct_size_text_input)
    LastFMusername = forms.CharField(max_length=50, required=False, widget=correct_size_text_input)

class SignupForm(forms.Form):
    # Putting these attrs here sucks, but I don't know how else to add all the attrs I want
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'required':True,'placeholder':'Username', 'class':'input-block-level'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'required':True,'placeholder':'Email', 'class':'input-block-level'}))
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={'required':True,'placeholder':'Password', 'class':'input-block-level'}))

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'required':True,'placeholder':'Username', 'class':'input-block-level'}))
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={'required':True,'placeholder':'Password', 'class':'input-block-level'}))
