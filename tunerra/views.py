from django.template import RequestContext
from django.shortcuts import render
from django import forms
from django.db import models
from tunerra.models import Song, Favorites, UserPreferences, Region
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import urllib
from xml.dom import minidom

last_fm_key = '61994d32a190d0a98684e84d6f38b41a'
fm_loved_str = 'http://ws.audioscrobbler.com/2.0/?method=user.getlovedtracks&user='
POPULARITY_CHOICE = {('1', 'Low Popularity'),
 ('2', 'Normal Popularity'), ('3', 'High Popularity')}



#Add songs
def parse_LastFM_love(xmltree, request):
    #print "WHOLE FILE: " + xmltree.toxml()
    for lfm in xmltree.getElementsByTagName('lfm'):
        for lovedSongs in xmltree.getElementsByTagName('lovedtracks'):
            for song in lfm.getElementsByTagName('track'):
                title = song.getElementsByTagName('name')[0].firstChild.nodeValue
                artist = song.getElementsByTagName('artist')[0].getElementsByTagName('name')[0].firstChild.nodeValue
                newSong = Song(title = title, artist = artist, album='noalb', year ='1999-01-22')
                newSong.save()
                newFav = Favorites()
                user = request.user
                hotness_level = 0
                song_id = newSong
                play_count = 1
                last_played = song.getElementsByTagName('date')[0].firstChild.nodeValue
                newFav = Favorites(user = user, hotness_level = hotness_level, song_id = song_id, play_count = play_count, last_played='1999-01-22')
                newFav.save()

                print "SONGS ARE: " + song.getElementsByTagName('name')[0].firstChild.nodeValue


def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/accounts/profile/'+request.user.username)
    else:
        # Treat them as anonymous user
        return render(request, 'index.html', RequestContext(request))

def login_error(request):
    return render(request, 'login_error.html', RequestContext(request))

def welcome(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login_error')
    prefForm = prefsForm(request.POST)
    if prefForm.is_valid():
        lastFMusername = prefForm.cleaned_data['LastFMusername']
        fm_str_req = fm_loved_str + lastFMusername + "&api_key=" + last_fm_key
        parse_LastFM_love(minidom.parse(urllib.urlopen(fm_str_req)), request) 
        notify_val = prefForm.cleaned_data['notify_system']
        region_val = prefForm.cleaned_data['region']

        newReg = Region(region_val)
        newReg.save()

        pop_val = prefForm.cleaned_data['popularity']
        genre_val = prefForm.cleaned_data['genre']
        user_pref = UserPreferences.objects.filter(user=request.user)
        if user_pref:
            # Update existing preferences
            user_pref.notify_system = notify_val
            user_pref.preferred_region = newReg
            user_pref.preferred_popularity = pop_val
            user_pref.preferred_genre = genre_val
            user_pref.save()
        else:
            # Create new userprefs
            newPrefs = UserPreferences(user = request.user, notify_system = notify_val,
            preferred_region = newReg, preferred_popularity = pop_val, preferred_genre = genre_val)
            newPrefs.save()



        return HttpResponseRedirect('/accounts/profile/'+request.user.username)
    else:
        return render(request, 'welcome.html', {'prefsForm': prefForm} )

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
                    return HttpResponseRedirect('/accounts/profile/'+login_username)
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

#Code to log into last FM

class prefsForm(forms.Form):
    notify_system = forms.BooleanField(required=False)
    region = forms.CharField(max_length=100)
    popularity = forms.ChoiceField(choices=POPULARITY_CHOICE)
    genre = forms.CharField(max_length=100)
    LastFMusername = forms.CharField(max_length=50)



def search(request):
    # TODO currently just sends to search page, should also populate with results
    return render(request, 'results.html', RequestContext(request))

def user_profile(request, username):
    if (request.user.is_authenticated() and request.user.username == username):
        return render(request, 'profile.html', RequestContext(request))
    else:
        logout(request)
        raise Http404

class SignupForm(forms.Form):
    # Putting these attrs here suck
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'required':True,'placeholder':'Username'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'required':True,'placeholder':'Email'}))
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={'required':True,'placeholder':'Password'}))

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'required':True,'placeholder':'Username'}))
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={'required':True,'placeholder':'Password'}))
