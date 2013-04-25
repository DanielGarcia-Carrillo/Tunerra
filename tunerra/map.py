import json
import math
from math import *
from django.shortcuts import render
from django.views.generic import View
from django.template import RequestContext
from django.http import Http404, HttpResponseBadRequest, HttpResponse, HttpResponseForbidden
from tunerra import models, views
from tunerra.models import Region, UserPreferences, Favorites, Song
from datetime import datetime
from json.encoder import JSONEncoder
from django.db.models import Count, Sum, Max


class UpdateMap(View):
    def __init__(self):
        self.latRange = 6.0
        self.lngRange = 20.0
        self.latLowerBoundDegree = 0.0
        self.latUpperBoundDegree = 0.0
        self.lngLowerBoundDegree = 0.0
        self.lngUpperBoundDegree = 0.0
    
    def post(self, request, *args, **kwargs):
        try:
            lat = float(request.POST['lat'])
            lng = float(request.POST['lng'])
            self.getBounds(lat,lng)
            print "lat lower = ", self.latLowerBoundDegree
            print "lat upper = ", self.latUpperBoundDegree
            print "lng lower = ", self.lngLowerBoundDegree
            print "lng upper = ", self.lngUpperBoundDegree
            print "after get bounds"
            
            regions = self.getRegionsInBounds()
            print regions
            print "got regions"
            userPrefs = UserPreferences.objects.filter(preferred_region__in=regions)
            print userPrefs
            print "got userprefs"
            try:
                favLst = []
                for prefs in userPrefs:
                    favLst.append(prefs.user)
                favs = Favorites.objects.filter(user__in = favLst)
                for fav in favs:
                    print fav
                    print fav.play_count
            except Exception as e:
                print e
            print "got favs"
            try:
                relation = favs.values('song_id').annotate(playcnt=Sum('play_count'))
            except Exception as e:
                print e
            print relation
            
            max = -1
            songID = None
            try:
                for song in relation:
                    print song
                    if song['playcnt'] > max:
                        songID = song['song_id']
                        max = song['playcnt']
            except Exception as e:
                print e
            
            
                    
            print songID
            print max
            try:
                mostPopSong = Song.objects.get(id = songID)
                print mostPopSong
            except Exception as e:
                print e
            
            response = HttpResponse()
            
            try:
                response.content = json.dumps({'lat': lat, 
                                               'lng': lng, 
                                               'title':mostPopSong.title,
                                               'artist': mostPopSong.artist.name,
                                               'album': mostPopSong.album.name, 
                                               'icon':mostPopSong.album.cover_art_url,
                                               })
            except Exception as e:
                print e
            print response.content
            return response
        except:
            return HttpResponseBadRequest()
        
    def getRegionsInBounds(self):
        if (self.latLowerBoundDegree > 0):
            rel1 = Region.objects.filter(lat__gte = self.latLowerBoundDegree).filter(lat__lte = self.latUpperBoundDegree)
        else:
            rel1 = Region.objects.filter(lat__lte = self.latLowerBoundDegree).filter(lat__gte = self.latUpperBoundDegree)
                
        if (self.lngLowerBoundDegree > 0):
            rel2 = rel1.filter(lng__gte = self.lngLowerBoundDegree).filter(lng__lte = self.lngUpperBoundDegree)
        else:
            rel2 = rel1.filter(lng__lte = self.lngLowerBoundDegree).filter(lng__gte = self.lngUpperBoundDegree)
            
        return rel2
    def makeCoordinateNormal(self, num, base):
        if (num > 0):
            print ">0,", num
            return num
        else:
            return base + num;
    
    def getBounds(self, lat, lng):
        
        latLowerIndex = math.floor((self.makeCoordinateNormal(lat, 180)) / self.latRange)
        lngLowerIndex = math.floor((self.makeCoordinateNormal(lng, 360)) / self.lngRange)

        if (latLowerIndex * self.latRange < 90.0):
            self.latLowerBoundDegree = latLowerIndex * self.latRange
        else:
            self.latLowerBoundDegree = 0 - ((latLowerIndex * self.latRange) % 90)
                
        if (lngLowerIndex * self.lngRange < 180.0):
            self.lngLowerBoundDegree = lngLowerIndex * self.lngRange
        else:
            self.lngLowerBoundDegree = 0 - ((lngLowerIndex * self.lngRange) % 180)
                
        if (self.latLowerBoundDegree < 0):
            self.latUpperBoundDegree = self.latLowerBoundDegree - self.latRange
        else:
            self.latUpperBoundDegree = self.latLowerBoundDegree + self.latRange
                
        if (self.lngLowerBoundDegree < 0):
            self.lngUpperBoundDegree = self.lngLowerBoundDegree - self.lngRange
        else:
            self.lngUpperBoundDegree = self.lngLowerBoundDegree + self.lngRange
            