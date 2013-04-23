#!/usr/bin/env python
import os
import requests

def setup_django_env(path):
    import imp
    from django.core.management import setup_environ

    f, filename, desc = imp.find_module('settings', [path])
    project = imp.load_module('settings', f, filename, desc)

    setup_environ(project)

def get_progress():
    try:
        f = open('.beatport_scraper_progress', 'r')
    except:
        return 0
    # There should only be one number written to the file, trim the newline
    first_line = f.read().strip()
    f.close()
    if first_line.isdigit():
        return int(first_line)
    return 0

def write_out_progress(iteration):
    progress_file = open('.beatport_scraper_progress', 'w')
    progress_file.write(str(iteration))
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
    existing_genre = Genre.objects.get(name=genre_name)
    if existing_genre:
        genre_record = existing_genre
    else:
        genre_record = Genre(name=genre_name, popularity=1)
        genre_record.save()
    return genre_record

def scrape_api_page(page_num):
    # 150 is the max number of tracks we can get per page
    request = requests.get('http://api.beatport.com/catalog/3/tracks?perPage=150&page='+str(x)+'&sortBy=trackName')
    if request.status_code == 200:
        # Put into db
        try:
            req_content = request.json()
        except:
            raise Exception("Json decoding failed")
            # Parsing based on: http://api.beatport.com/catalog-object-structures.html for track
        results = req_content['results']
        for track in results:
            # Some tracks have no artist, we don't want these tracks
            if len(track['artists']) < 1:
                continue
                # Hacky way to deal with tracks with multiple artists, ie just get first artist
            artist = track['artists'][0]['name']
            album = track['release']['name']
            image_url = track['images']['large']['secureUrl']
            year = track['releaseDate']

            provider_id = track['id']
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
                                   provider_track_id=provider_id
                )
                song_record.save()

    else:
        raise Exception('Bad request at iteration: ' + str(x))

if __name__ == '__main__':
    import traceback
    setup_django_env(os.path.dirname(os.path.abspath("."))+"/myproject")

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
        try:
            scrape_api_page(x)
        except Exception as exc:
            print exc
            traceback.print_exc()
            write_out_progress(x)
            break