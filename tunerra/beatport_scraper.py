#!/usr/bin/env python
from django.conf import settings
import requests
def setup_django_env(path):
    import imp, os
    from django.core.management import setup_environ

    f, filename, desc = imp.find_module('settings', [path])
    project = imp.load_module('settings', f, filename, desc)

    setup_environ(project)

def get_progress():
    try:
        f = open('.beatport_scraper_progress', 'r')
    except:
        return 0
    return int(f.read())

def write_out_progress(iteration):
    progress_file = open('.beatport_scraper_progress', 'w')
    progress_file.write(iteration)
    progress_file.close()

def save_artist(artist_name):
    """
    If the artist doesn't exist, saves it to the database and returns it. Returns existing artist record otherwise
    """
    artist_record = None
    if not Artist.objects.filter(name=artist_name):
        artist_record = Artist(name=artist_name)
        artist_record.save()
    else:
        artist_record = Artist.objects.filter(name=artist_name)[0]

    return artist_record

def save_album(album_name, cover_url, release_year):
    album_record = None
    if not Album.objects.filter(name=album_name):
        album_record = Album(name=album_name, cover_art_url=cover_url, year=release_year)
        album_record.save()
    else:
        album_record = Album.objects.filter(name=album_name)[0]

    return album_record

def save_genre(genre_name):
    existing_genre = Genre.objects.filter(name=genre_name)
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
    return genre_record

if __name__ == '__main__':
    # TODO absolute path
    setup_django_env('/Users/Daniel/Tunerra/myproject')

    from tunerra.models import Song, Genre, MetadataProvider, Album, Artist
    # We are scraping Beatport. Add it to the list of providers if it's not present
    metadata_provider = MetadataProvider.objects.filter(name="Beatport")
    if metadata_provider:
        metadata_provider = metadata_provider[0]
    else:
        metadata_provider = MetadataProvider(name="Beatport")
        metadata_provider.save()

    initial_page = get_progress()
    for x in range(initial_page, 17894):  # 17894 is the last beatport page
        # 150 is the max number of tracks we can get per page
        req = requests.get('http://api.beatport.com/catalog/3/tracks?perPage=150&page='+str(x)+'&sortBy=trackName')
        if req.status_code == 200:
            # Put into db
            try:
                req_content = req.json()
            except:
                print "Json decoding failed"
                break
            # Parsing based on: http://api.beatport.com/catalog-object-structures.html for track
            results = req_content['results']
            for track in results:
                # Some tracks have no artist or genre, we don't want these tracks
                if len(track['artists']) < 1:
                    continue
                # Hacky way to deal with tracks with multiple artists, ie just get first artist
                artist = track['artists'][0]['name']
                album = track['release']['name']
                image_url = track['images']['large']['secureUrl']
                year = track['releaseDate']

                id = track['id']
                title = track['title']
                track_number = track['trackNumber']
                bpm = track['bpm']
                length = track['length']
                genre = track['genres'][0]['name'].lower()

                # apparently the following condition is required, you can remove it if you like pain
                if len(artist)>100 or len(album)>100 or len(title)>100 or len(length) > 6:
                    continue
                artist_record = save_artist(artist)
                album_record = save_album(album,image_url,year)

                genre_record = save_genre(genre)

                exact_song_matches = Song.objects.filter(title=title,artist=artist_record)
                if not exact_song_matches:
                    # Setting 0 popularity because TODO
                    song_record = Song(title=title,
                                       artist=artist_record,
                                       album=album_record,
                                       genre=genre_record,
                                       popularity=0,
                                       bpm=bpm,
                                       length=length,
                                       track_number=track_number,
                                       provider=metadata_provider,
                                       provider_track_id=id
                                       )
                    song_record.save()

        else:
            print "Something went wrong at iteration: " + str(x)
            break