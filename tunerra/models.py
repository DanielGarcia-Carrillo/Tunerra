from django.db import models
from django.contrib.auth.models import User


class Region(models.Model):
    name = models.CharField(max_length=100, primary_key=True, unique=True)

    def __unicode__(self):
        return self.name


class UserPreferences(models.Model):
    user = models.OneToOneField(User)
    notify_system = models.CharField(max_length=100)
    preferred_region = models.ForeignKey(Region)
    preferred_popularity = models.CharField(max_length=100)
    preferred_genre = models.CharField(max_length=100)
    last_fmName = models.CharField(max_length=300)

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    popularity = models.DecimalField(max_digits=10, decimal_places=6, default = 0)
    def __unicode__(self):
        return self.name

class Album(models.Model):
    name = models.CharField(max_length=100, unique=True)
    cover_art_url = models.URLField()
    year = models.DateField(auto_now=False)

    def __unicode__(self):
        return u"%s %s" % (self.name, self.year)


class Artist(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name


class MetadataProvider(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.name


class Song(models.Model):
    title = models.CharField(max_length=100)
    album = models.ForeignKey(Album)
    artist = models.ForeignKey(Artist)
    popularity = models.DecimalField(max_digits=10, decimal_places=6, default = 0)
    genre = models.ForeignKey(Genre)
    track_number = models.IntegerField(max_length=5, default = 0)
    bpm = models.IntegerField(max_length=4, default = 0)
    length = models.CharField(max_length=8, default = 0)
    provider = models.ForeignKey(MetadataProvider)
    provider_track_id = models.CharField(max_length=100)
    class Meta:
        unique_together=['artist', 'title']

    def __unicode__(self):
        return u'%s - %s - %s' % (self.title, self.album.name, self.artist.name)


class Recommendation(models.Model):
    user = models.ForeignKey(User)
    creation_time = models.DateTimeField(auto_now_add=True)
    user_liked = models.BooleanField()

    class Meta:
        abstract = True


class MusicRecommendation(Recommendation):
    song = models.ForeignKey(Song)


class FollowRecommendation(Recommendation):
    follow_user = models.ForeignKey(User, related_name="follow_user")


class Post(models.Model):
    user = models.ForeignKey(User)
    song = models.ForeignKey(Song)
    likes = models.IntegerField()
    creation_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s %s %d %s" % (self.user.name, self.song.title, self.likes, self.creation_time)


class Favorites(models.Model):
    user = models.ForeignKey(User)
    hotness_level = models.IntegerField(default = 0)
    song_id = models.ForeignKey(Song)
    play_count = models.IntegerField(default = 0)
    last_played = models.DateTimeField(null=True)
    class Meta:
        unique_together=['user', 'song_id']


class Like(models.Model):
    user = models.ForeignKey(User)
    liked_post = models.ForeignKey(Post)


class Follows(models.Model):
    user = models.ForeignKey(User, related_name='follow_src')
    following = models.ForeignKey(User, related_name='follow_dst')

    def __unicode__(self):
        return u"%s -> %s" % (self.user.username, self.following.username)

    # Not sure if this is necessary because there are only two attributes in the table
    class Meta:
        unique_together = ['user', 'following']
