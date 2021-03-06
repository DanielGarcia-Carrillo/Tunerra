from django.db import models
from django.contrib.auth.models import User
import datetime


class Region(models.Model):
    name = models.CharField(max_length=100, primary_key=True, unique=True)
    lat = models.FloatField(default = 42.0)
    lng = models.FloatField(default = -88.0)

    def __unicode__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    popularity = models.DecimalField(max_digits=10, decimal_places=6, default = 0)

    def __unicode__(self):
        self.name = self.name
        return self.name


class UserPreferences(models.Model):
    user = models.OneToOneField(User)
    notify_system = models.CharField(max_length=100)
    preferred_region = models.ForeignKey(Region)
    preferred_popularity = models.CharField(max_length=100)
    last_fmName = models.CharField(max_length=300)

    def __unicode__(self):
        return str(self.user)


class UserPreferredGenre(models.Model):
    user = models.ForeignKey(User)
    genre = models.ForeignKey(Genre)
    weight = models.FloatField(default = 1.0)

    def save(self, *args, **kwargs):
        if self.weight > 1.0:
            self.weight = models.FloatField(1.0)
        elif self.weight < 0.0:
            self.weight = models.FloatField(0.0)
        super(UserPreferredGenre, self).save(*args, **kwargs)


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
    title = models.CharField(max_length=200)
    album = models.ForeignKey(Album)
    artist = models.ForeignKey(Artist)
    popularity = models.DecimalField(max_digits=10, decimal_places=6, default = 0)
    genre = models.ForeignKey(Genre)
    track_number = models.IntegerField(max_length=5, default = 0)
    bpm = models.IntegerField(max_length=4, default = 0)
    length = models.CharField(max_length=20, default="00:00")
    provider = models.ForeignKey(MetadataProvider)
    provider_track_id = models.CharField(max_length=100)
    class Meta:
        unique_together=['artist', 'title']

    def __unicode__(self):
        return u'%s - %s - %s' % (self.title, self.album.name, self.artist.name)


class Recommendation(models.Model):
    user = models.ForeignKey(User)
    creation_time = models.DateTimeField(auto_now_add=True)
    user_liked = models.NullBooleanField()

    class Meta:
        abstract = True


class MusicRecommendation(Recommendation):
    song = models.ForeignKey(Song)


class FollowRecommendation(Recommendation):
    follow_user = models.ForeignKey(User, related_name="follow_user")


class Post(models.Model):
    user = models.ForeignKey(User)
    song = models.ForeignKey(Song)
    likes = models.IntegerField(default=0)
    body = models.CharField(default="", max_length=1500)
    creation_time = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """ save will add song to favorites if it's not there and increment playcount if it is """
        if Favorites.objects.filter(user = self.user, song_id = self.song):
            currFav = Favorites.objects.get(user = self.user, song_id = self.song)
            currFav.play_count += 1
            currFav.last_played = datetime.datetime.now().strftime("%Y-%m-%d")
            currFav.save()
            super(Post, self).save(*args, **kwargs)
            return
        fav, created = Favorites.objects.get_or_create(user=self.user, song_id=self.song, last_played = datetime.datetime.now().strftime("%Y-%m-%d"))
        if not created:
            fav.play_count += 1

        #fav.last_played = self.creation_time
        fav.save()

        super(Post, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s %s %d %s" % (self.user.username, self.song.title, self.likes, self.creation_time)


class Favorites(models.Model):
    user = models.ForeignKey(User)
    hotness_level = models.IntegerField(default = 0)
    song_id = models.ForeignKey(Song)
    play_count = models.IntegerField(default=1)
    last_played = models.DateTimeField(null=True)

    def __unicode__(self):
        return str(self.user) + " <3 " + str(self.song_id)

    class Meta:
        unique_together=['user', 'song_id']



class Like(models.Model):
    user = models.ForeignKey(User)
    liked_post = models.ForeignKey(Post)

    def save(self, *args, **kwargs):
        """
        the current record doesn't have a pk if it's just being created
        (we only want to increment likes when it's a new like)
        """
        if not self.pk:
            self.liked_post.likes += 1
            self.liked_post.save()
        super(Like, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.liked_post.likes -= 1
        self.liked_post.save()
        super(Like, self).delete(*args, **kwargs)

    def __unicode__(self):
        return u"%s likes post %d" % (self.user.username, self.liked_post.pk)


class Follows(models.Model):
    user = models.ForeignKey(User, related_name='follow_src')
    following = models.ForeignKey(User, related_name='follow_dst')

    def __unicode__(self):
        return u"%s -> %s" % (self.user.username, self.following.username)

    def save(self, *args, **kwargs):
        try:
            rec = FollowRecommendation.objects.get(user=self.user, follow_user=self.following)
            rec.delete()
        except:
            pass
        super(Follows, self).save(*args, **kwargs)

    # Not sure if this is necessary because there are only two attributes in the table
    class Meta:
        unique_together = ['user', 'following']
