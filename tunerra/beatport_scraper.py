#!/usr/bin/env python
from django.conf import settings
import requests
def setup_django_env(path):
    import imp, os
    from django.core.management import setup_environ

    f, filename, desc = imp.find_module('settings', [path])
    project = imp.load_module('settings', f, filename, desc)

    setup_environ(project)

if __name__ == '__main__':
    # TODO absolute path
    setup_django_env('/Users/Daniel/Tunerra/myproject')

    from tunerra.models import Song, Genre
    for x in range(200):
        # 150 is the max number of tracks we can get per page
        req = requests.get('http://api.beatport.com/catalog/3/tracks?perPage=150&page='+str(x)+'&sortBy=trackName')
        if req.status_code == 200:
            #Put into db
            try:
                req_content = req.json()
            except:
                print "Json decoding failed"
                break
            # Parsing based on: http://api.beatport.com/catalog-object-structures.html for track
            results = req_content['results']
            for track in results:
                title = track['title']
                # Some tracks have no artist or genre, we don't want these tracks
                if len(track['artists']) < 1 or len(track['genres']) < 1:
                    continue
                # Hacky way to deal with tracks with multiple artists, ie just get first artist
                artist = track['artists'][0]['name']
                genre = track['genres'][0]['name'].lower()
                album = track['release']['name']
                year = track['releaseDate']
                # apparently the following condition is required, you can remove it if you like pain
                if (len(artist)>100 or len(album)>100 or len(title)>100):
                    continue
                # Check if genre exists and save (TODO would probably be better to do this in memory then commit transaction)
                existing_genre = Genre.objects.filter(name=genre)
                genre_record = None
                if existing_genre:
                    # There should only be one exact match because name is unique
                    existing_genre = existing_genre[0]
                    # Here I'm defining popularity by the number of tracks with that genre
                    existing_genre.popularity += 1
                    existing_genre.save()
                    genre_record = existing_genre
                else:
                    genre_record = Genre(name=genre, popularity=1)
                    genre_record.save()

                exact_song_matches = Song.objects.filter(title=title,artist=artist)
                if not exact_song_matches:
                    # Setting 0 popularity because TODO
                    song_record = Song(title=title, artist=artist, album=album, year=year, genre=genre_record, popularity=0)
                    song_record.save()

        else:
            print "Something went wrong at iteration: " + str(x)
            break