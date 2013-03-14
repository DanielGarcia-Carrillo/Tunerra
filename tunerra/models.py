from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class SiteUser(models.Model):
    user = models.OneToOneField(User)
    user_id = models.AutoField(primary_key=True)
    location = models.CharField(max_length=100)


class Region(models.Model):
    name = models.CharField(max_length=100, primary_key=True)


class UserPreferences(models.Model):
    user = models.ForeignKey(SiteUser)
    notify_system = models.CharField(max_length=100)
    preferred_region = models.ForeignKey(Region)
    preferred_popularity = models.CharField(max_length=100)
    preferred_genre = models.CharField(max_length=100)

class Song(models.Model):
    song_id = models.IntegerField(primary_key=True)
    artist = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    album = models.CharField(max_length=100)
    year = models.DateField(auto_now=False, auto_now_add=False)


class Favorites(models.Model):
    user = models.ForeignKey(SiteUser)
    hotness_level = models.IntegerField()
    song_id = models.ForeignKey(Song)
    play_count = models.IntegerField()
    last_played = models.DateTimeField()


