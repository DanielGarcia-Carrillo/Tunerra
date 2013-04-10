from django.db import models
from django.contrib.auth.models import User


class Region(models.Model):
    name = models.CharField(max_length=100, primary_key=True, unique=True)

class UserPreferences(models.Model):
    user = models.OneToOneField(User)
    notify_system = models.CharField(max_length=100)
    preferred_region = models.ForeignKey(Region)
    preferred_popularity = models.CharField(max_length=100)
    preferred_genre = models.CharField(max_length=100)
    last_fmName = models.CharField(max_length=300)

class Genre(models.Model):
  name = models.CharField(max_length=100, unique=True)
  popularity = models.DecimalField(max_digits=10, decimal_places=6)
  parentGenre = models.ForeignKey('self')

class Song(models.Model):
    artist = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    album = models.CharField(max_length=100, null=True)
    year = models.DateField(auto_now = False)
    popularity = models.DecimalField(max_digits=10, decimal_places=6)
    genre = models.ForeignKey(Genre)
    class Meta:
        unique_together=['artist', 'title']

class Post(models.Model):
  user = models.ForeignKey(User)
  title = models.CharField(max_length=1500)
  song = models.ForeignKey(Song)
  likes = models.IntegerField()

class Favorites(models.Model):
    user = models.ForeignKey(User)
    hotness_level = models.IntegerField()
    song_id = models.ForeignKey(Song)
    play_count = models.IntegerField()
    last_played = models.DateTimeField(null=True)
    class Meta:
        unique_together=['user', 'song_id']

class Follows(models.Model):
  user = models.ForeignKey(User, related_name = 'Follows_source')
  following = models.ForeignKey(User, related_name = 'Follows_dest')
