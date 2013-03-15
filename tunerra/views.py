from django.template import RequestContext
from django.shortcuts import render
from django import forms
from django.db import models
from tunerra.models import Song, Favorites, UserPreferences, Region
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate
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
    return render(request,'index.html', RequestContext(request))

class SignupForm(forms.Form):
    #def __init__(self, *args):
    #    super(SignupForm, self).__init__(args, auto_id='id_signup_%s')
    # Putting these attrs here suck
    username = forms.CharField(max_length=30, min_length=5,widget=forms.TextInput(attrs={'required':True,'placeholder':'Username'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'required':True,'placeholder':'Email'}))
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={'required':True,'placeholder':'Password'}))

class LoginForm(forms.Form):
    #def __init__(self, *args):
    #    super(LoginForm, self).__init__(args, auto_id='id_login_%s')
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'required' : True,'placeholder':'Username'}))
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={'required':True,'placeholder':'Password'}))

def logout(request):
    logout(request)
    return redirect(request, 'index.html')

def welcome(request):
    if not request.user.is_authenticated():
        return redirect(request, 'login_error.html')
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
        newPrefs = UserPreferences(user = request.user, notify_system = notify_val,
            preferred_region = newReg, preferred_popularity = pop_val, preferred_genre = genre_val)
        newPrefs.save()



        return HttpResponse()
    else:
        return render(request, 'welcome.html', {'prefsForm': prefForm} )

def login_signup(request):
    if request.method == 'POST':
        # Hacky way to tell which form is being POSTed
        signup_form = SignupForm(request.POST)
        login_form = LoginForm(request.POST)
        if signup_form.is_valid():
            new_user = User.objects.create_user(
                username=signup_form.cleaned_data['username'],
                email=signup_form.cleaned_data['email'],
                password=signup_form.cleaned_data['password']
            )
            #if new_user is None:
                # TODO do something about this, means that user exists already

            return HttpResponseRedirect('/accounts/welcome')
        elif login_form.is_valid():
            user = authenticate(username=login_form.username, password=login_form.password)
            if user is None:
                # Return error
                return HttpResponse()
            else:
                # Send to profile
                return HttpResponse()
        else:
            # TODO make this discriminant of which form was POSTed
            return render(request, 'accounts.html', {'signup_form':signup_form, 'login_form':login_form})
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



