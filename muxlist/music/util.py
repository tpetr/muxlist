import urllib, urllib2
from mutagen.easyid3 import EasyID3

def get_track_data_from_url(url):
    request = urllib2.Request(url)

    byte_count = 500

    while True:
        print "Trying %s bytes" % byte_count
        request.add_header('Range', 'bytes=0-%s' % byte_count)

        response = urllib2.urlopen(request)

        fp = open("/tmp/test.mp3", "wb")
        fp.write(response.read())
        fp.close()

        try:
            audio = EasyID3("/tmp/test.mp3")
            break
        except EOFError:
            byte_count += 10000

    try:
        artist = audio['artist']
        if isinstance(artist, list): artist = artist[0]
    except KeyError:
        artist = "(Unknown Artist)"

    try:
        album = audio.get('album', '')
        if isinstance(album, list): album = album[0]
    except KeyError:
        album = "(Unknown Album)"

    try:
        title = audio['title']
        if isinstance(title, list): title = title[0]
    except KeyError:
        title = "(Unknown Title)"

    try:
        year = audio.get('date', None)
        if isinstance(year, list): year = year[0]
    except KeyError:
        year = "2010"

    return (artist, album, title, year, None)




def get_track_data_from_file(filename):
    audio = EasyID3(filename)

    try:
        artist = audio['artist']
        if isinstance(artist, list): artist = artist[0]
    except KeyError:
        artist = "(Unknown Artist)"

    try:
        album = audio.get('album', '')
        if isinstance(album, list): album = album[0]
    except KeyError:
        album = "(Unknown Album)"

    try:
        title = audio['title']
        if isinstance(title, list): title = title[0]
    except KeyError:
        title = "(Unknown Title)"

    try:
        year = audio.get('date', None)
        if isinstance(year, list): year = year[0]
    except KeyError:
        year = "2010"

    return (artist, album, title, year, None)
