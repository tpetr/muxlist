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

    artist = audio['artist']
    if isinstance(artist, list): artist = artist[0]

    album = audio.get('album', '')
    if isinstance(album, list): album = album[0]

    title = audio['title']
    if isinstance(title, list): title = title[0]

    year = audio.get('date', None)
    if isinstance(year, list): year = year[0]

    return (artist, album, title, year, None)
