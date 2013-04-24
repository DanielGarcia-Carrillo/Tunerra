#!/usr/bin/env python
from django.conf import settings
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import BaseHTTPServer
from cgi import parse_header, parse_multipart
from django.contrib.auth import authenticate
from urlparse import parse_qs
import datetime
import traceback
import urllib2
import json
import requests
import socket
import sys
import Queue
import time
import thread

lastFmLink_Track = 'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key=64e400a9de3b4287b61df31a91237cb3&artist=!&track=$&format=json'
lastFmLink_Album = 'http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key=64e400a9de3b4287b61df31a91237cb3&artist=!&album=$&format=json'


DjangoPortNum = 14689
TCP_IP = '127.0.0.1'
BUFFER_SIZE = 1024 * 1000

sys.path.append(R"C:\Coding\Django\virtualenv-1.8.4\my_env\Scripts\myproject")

def setup_django_env(path):
    import imp, os
    from django.core.management import setup_environ

    f, filename, desc = imp.find_module('settings', [path])
    project = imp.load_module('settings', f, filename, desc)

    print project

    setup_environ(project)

def setupServer():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((TCP_IP, DjangoPortNum))
	s.listen(1)
	return s
	
	
def acceptConnection(s):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((TCP_IP, DjangoPortNum))
	s.listen(1)
	return s.accept()

class importHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        q = Queue.Queue()
        print "Got response!"
        self.send_response(200)
        self.end_headers()
        length = int(self.headers.getheader('content-length'))
        postvars = json.loads(self.rfile.read(length))
        numSongs = 0
        loginInfo = postvars.pop(0)
        username = loginInfo['username']
        password = loginInfo['password']
        for songItem in postvars:
            q.put(songItem)
        thread.start_new_thread(validate, (username, password, q))





def run(server_class = BaseHTTPServer.HTTPServer, handler_class = importHandler):
    server_address = ('', 14689)
    httpd = server_class(server_address, handler_class)
    print "waiting for incoming connection..."
    httpd.serve_forever()


def validate(username, password, q):
    songsAdded = 0
    i = -1
    user = authenticate(username=username, password=password)
    if user is None:
        print "User " + username + " validated."
    else:
        print "User " + username + " not validated."
    while not q.empty():
        songItem = q.get()
        name = songItem['title'].strip()
        artist = songItem['artist'].strip()
        artistobj = None
        if Artist.objects.filter(name = artist).exists():
            artistobj = Artist.objects.get(name = artist)
            if Song.objects.filter(title = name, artist = artistobj).exists():
                print "Song already in database quickly: " + name + ' - ' + artist
                continue
        name = name.replace(' ', '+')
        artist = artist.replace(' ', '+')
        if i == 1:
            time.sleep(1)
        i = -i
        newLink = lastFmLink_Track.replace('!', artist).replace('$', name).replace(' ', '')
        req = urllib2.Request(newLink)
        head = urllib2.build_opener()
        try:
            jsonSong = json.load(head.open(req))        
        except: continue
        if 'error' in jsonSong:
            continue
        trackInfo = jsonSong['track']
        try:
            if not Artist.objects.filter(name = trackInfo['artist']['name']).exists():
                songsAdded = addToDatabase(trackInfo, songsAdded)
                continue
        except:
            print "ERROR!"
            continue
        currArtist = Artist.objects.filter(name = trackInfo['artist']['name'])[0]
        if Song.objects.filter(title = trackInfo['name'], artist = currArtist).exists():
            print "Song already in database: " + trackInfo['name']
            continue
        songsAdded = addToDatabase(trackInfo, songsAdded)
    print "Added " + str(songsAdded) + " songs to database!"
        

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
        newAlb, created = Album.objects.get_or_create(**albumDict)
        newGenre, created = Genre.objects.get_or_create(name = songDict['genre'])
        newArtist, created = Artist.objects.get_or_create(name = songDict['artist'])
        newProvider, created = MetadataProvider.objects.get_or_create(name = songDict['provider'])
        songDict['genre'] = newGenre
        songDict['artist'] = newArtist
        songDict['album'] = newAlb
        songDict['provider'] = newProvider
        Song(**songDict).save()
        print "Added song " + trackInfo['name'] + ' - ' + trackInfo['artist']['name'] + ' to database'
        return songsAdded + 1
    except Exception as e:
        print e
        print traceback.print_exc()
        print "Error adding song!" 
        return songsAdded


	
if __name__ == '__main__':
    # TODO absolute path
    setup_django_env(R'C:/Coding/Django/virtualenv-1.8.4/my_env/Scripts/myproject/myproject')	
    from tunerra.models import Song, Album, Artist, Genre, MetadataProvider
    from django.db import transaction
    run()
	
	