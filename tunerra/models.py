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

class Album(models.Model):
    name = models.CharField(max_length=100, unique=True)
    cover_art_url = models.URLField()
    year = models.DateField(auto_now=False)

class Artist(models.Model):
    name = models.CharField(max_length=100, unique=True)

class MetadataProvider(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Song(models.Model):
    title = models.CharField(max_length=100)
    album = models.ForeignKey(Album)
    artist = models.ForeignKey(Artist)
    popularity = models.DecimalField(max_digits=10, decimal_places=6)
    genre = models.ForeignKey(Genre)
    track_number = models.IntegerField(max_length=5)
    bpm = models.IntegerField(max_length=4)
    length = models.CharField(max_length=8)
    provider = models.ForeignKey(MetadataProvider)
    provider_track_id = models.CharField(max_length=100)
    class Meta:
        unique_together=['artist', 'title']

    def __unicode__(self):
        return u'%s - %s - %s' % (self.title, self.album.name, self.artist.name)


class Post(models.Model):
    TYPES = (
        ('U', 'User post'),
        ('M', 'Music recommendation'),
        ('F', 'Follow recommendation'),
    )
    user = models.ForeignKey(User)
    body = models.CharField(max_length=1500)
    likes = models.IntegerField()
    creation_time = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=2, choices=TYPES)
    song = models.ForeignKey(Song, null=True)
    follow_rec = models.ForeignKey(User, null=True, related_name="follow_rec")

    # These are constraints on the model to make sure that one recommendation field is null if the other type is used
    def save(self, *args, **kwargs):
        if (self.type == 'U' and not self.song and not self.follow_rec) or \
        (self.type == 'M' and self.song and not self.follow_rec) or \
        (self.type == 'F' and not self.song and self.follow_rec):
            super(Post, self).save()
        else:
            raise Exception, "This is not a valid post"


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
