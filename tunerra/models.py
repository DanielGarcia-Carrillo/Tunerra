from django.db import models
from django.contrib.auth.models import User


"""CREATE TABLE tunerra_region
(
  name character varying(100) NOT NULL,
  CONSTRAINT tunerra_region_pkey PRIMARY KEY (name)
)"""
class Region(models.Model):
    name = models.CharField(max_length=100, primary_key=True, unique=True)

"""CREATE TABLE tunerra_userpreferences
(
  id serial NOT NULL,
  user_id integer NOT NULL,
  notify_system character varying(100) NOT NULL,
  preferred_region_id character varying(100) NOT NULL,
  preferred_popularity character varying(100) NOT NULL,
  preferred_genre character varying(100) NOT NULL,
  CONSTRAINT tunerra_userpreferences_pkey PRIMARY KEY (id),
  CONSTRAINT tunerra_userpreferences_preferred_region_id_fkey FOREIGN KEY (preferred_region_id)
      REFERENCES tunerra_region (name) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT tunerra_userpreferences_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES auth_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT tunerra_userpreferences_user_id_key UNIQUE (user_id)
)"""

class UserPreferences(models.Model):
    user = models.OneToOneField(User)
    notify_system = models.CharField(max_length=100)
    preferred_region = models.ForeignKey(Region)
    preferred_popularity = models.CharField(max_length=100)
    preferred_genre = models.CharField(max_length=100)


"""
CREATE TABLE tunerra_song
(
  id serial NOT NULL,
  artist character varying(100) NOT NULL,
  title character varying(100) NOT NULL,
  album character varying(100) NOT NULL,
  year date NOT NULL,
  CONSTRAINT tunerra_song_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE tunerra_song
  OWNER TO main;
  """

class Song(models.Model):
    artist = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    album = models.CharField(max_length=100, null=True)
    year = models.DateField(auto_now = False)
    class Meta:
        unique_together=['artist', 'title']


"""CREATE TABLE tunerra_favorites
(
  id serial NOT NULL,
  user_id integer NOT NULL,
  hotness_level integer NOT NULL,
  song_id_id integer NOT NULL,
  play_count integer NOT NULL,
  last_played timestamp with time zone NOT NULL,
  CONSTRAINT tunerra_favorites_pkey PRIMARY KEY (id),
  CONSTRAINT tunerra_favorites_song_id_id_fkey FOREIGN KEY (song_id_id)
      REFERENCES tunerra_song (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT tunerra_favorites_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES auth_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
"""
class Favorites(models.Model):
    user = models.ForeignKey(User)
    hotness_level = models.IntegerField()
    song_id = models.ForeignKey(Song)
    play_count = models.IntegerField()
    last_played = models.DateTimeField(null=True)
    class Meta:
        unique_together=['user', 'song_id']


