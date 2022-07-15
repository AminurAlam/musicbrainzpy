"""
A basic MusicBrainz API wrapper
"""

__version__ = "1.2.0"
__author__ = "AminurAlam"

import json
import requests

mbz_root_url = "https://musicbrainz.org/ws/2"
caa_root_url = "https://coverartarchive.org"


# ====================
# cover art archive
# ====================

def caa_req(entity: str, mbid: str) -> dict:
    """
    common status codes:
        307 redirect to an index.json file, if there is a release with this MBID.
        400 if {mbid} cannot be parsed as a valid UUID.
        404 if there is no release with this MBID.
        405 if the request method is not one of GET or HEAD.
        406 if the server is unable to generate a response.
        503 if the user has exceeded their rate limit
    """
    caa_url = f"{caa_root_url}/{entity}/{mbid}"
    response = requests.get(caa_url)

    try:
        return json.loads(response.content.decode())
    except Exception as error:
        return {"response": response, "error": error}

def release_art(mbid: str):
    return caa_req("release", mbid)
def release_group_art(mbid: str):
    return caa_req("release-group", mbid)

# ============
# searching
# ============

def search(entity: str, query: str, limit: int, offset: int) -> dict:
    """
    there are 13 resources which represent core entities:
        area, artist, event, genre, instrument, label, place,
        recording, release, release-group, series, work, url
    these are non-core resources:
        rating, tag, collection
    search documentation:
        https://musicbrainz.org/doc/MusicBrainz_API/Search
    search query:
        /<ENTITY_TYPE>?query=<QUERY>&limit=<LIMIT>&offset=<OFFSET>
    """
    params = {
        "query": query,
        "limit": str(limit),
        "offset": str(offset),
        "fmt": "json"}
    url = f"{mbz_root_url}/{entity}"
    response = requests.get(url, params=params)

    return json.loads(response.content.decode())

def search_area(query: str, limit: int, offset: int):
    return search("area", query, limit, offset)
def search_artist(query: str, limit: int, offset: int):
    return search("artist", query, limit, offset)
def search_event(query: str, limit: int, offset: int):
    return search("event", query, limit, offset)
def search_genre(query: str, limit: int, offset: int):
    return search("genre", query, limit, offset)
def search_instrument(query: str, limit: int, offset: int):
    return search("instrument", query, limit, offset)
def search_label(query: str, limit: int, offset: int):
    return search("label", query, limit, offset)
def search_place(query: str, limit: int, offset: int):
    return search("place", query, limit, offset)
def search_recording(query: str, limit: int, offset: int):
    return search("recording", query, limit, offset)
def search_release(query: str, limit: int, offset: int):
    return search("release", query, limit, offset)
def search_release_group(query: str, limit: int, offset: int):
    return search("release-group", query, limit, offset)
def search_series(query: str, limit: int, offset: int):
    return search("series", query, limit, offset)
def search_work(query: str, limit: int, offset: int):
    return search("work", query, limit, offset)
def search_url(query: str, limit: int, offset: int):
    return search("url", query, limit, offset)

def search_collection(query: str, limit: int, offset: int):
    return search("collection", query, limit, offset)
def search_rating(query: str, limit: int, offset: int):
    return search("rating", query, limit, offset)
def search_tag(query: str, limit: int, offset: int):
    return search("tag", query, limit, offset)



# =========
# lookup
# =========

def lookup(entity: str, mbid: str, inc: str):
    """
    lookup entities to be added:
        area, collection, event, genre,
        instrument, place, series, work, url
    some additional 'inc=' parameters:
        discids, media, isrcs, artist-credits, various-artists
    misc 'inc=' arguments:
        aliases, annotation, tags, ratings, user-tags,
        user-ratings, genres, user-genres
    """
    params = {
        "inc": inc,
        "fmt": "json"}
    url = f"{mbz_root_url}/{entity}/{mbid}"
    response = requests.get(url, params=params)

    return json.loads(response.content.decode())

def lookup_area(mbid: str, inc: str = ""):
    return lookup("area", mbid, inc)
def lookup_artist(mbid: str, inc: str = "recordings+releases+release-groups+works"):
    return lookup("artist", mbid, inc)
def lookup_collection(mbid: str, inc: str = "user-collections"):
    return lookup("collection", mbid, inc)
def lookup_event(mbid: str, inc: str = ""):
    return lookup("event", mbid, inc)
def lookup_genre(mbid: str, inc: str = ""):
    return lookup("genre", mbid, inc)
def lookup_instrument(mbid: str, inc: str = ""):
    return lookup("instrument", mbid, inc)
def lookup_label(mbid: str, inc: str = "releases"):
    return lookup("label", mbid, inc)
def lookup_place(mbid: str, inc: str = ""):
    return lookup("place", mbid, inc)
def lookup_recording(mbid: str, inc: str = "artists+releases+isrcs+url-rels"):
    return lookup("recording", mbid, inc)
def lookup_release(mbid: str, inc: str = "artists+collections+labels+recordings+release-groups"):
    return lookup("release", mbid, inc)
def lookup_release_group(mbid: str, inc: str = "artists+releases"):
    return lookup("release-group", mbid, inc)
def lookup_series(mbid: str, inc: str = ""):
    return lookup("series", mbid, inc)
def lookup_work(mbid: str, inc: str = ""):
    return lookup("work", mbid, inc)
def lookup_url(mbid: str, inc: str = ""):
    return lookup("url", mbid, inc)

def lookup_discid(id: str, inc: str = ""):
    return lookup("discid", id, inc)
def lookup_isrc(id: str, inc: str = ""):
    return lookup("isrc", id, inc)
def lookup_iswc(id: str, inc: str = ""):
    return lookup("iswc", id, inc)


# =========
# browse
# =========

def browse(entity: str, mbid: str, inc: str):
    """
    docstring
    """
    params = {
        "mbid": mbid,
        "inc": inc,
        "fmt": "json"}
    url = f"{mbz_root_url}/{entity}"
    response = requests.get(url, params=params)

    return json.loads(response.content.decode())

def browse_area(mbid: str, inc: str = ""):
    return browse("area", mbid, inc)
def browse_artist(mbid: str, inc: str = ""):
    return browse("artist", mbid, inc)
def browse_collection(mbid: str, inc: str = ""):
    return browse("collection", mbid, inc)
def browse_event(mbid: str, inc: str = ""):
    return browse("event", mbid, inc)
def browse_genre(mbid: str, inc: str = ""):
    return browse("genre", mbid, inc)
def browse_instrument(mbid: str, inc: str = ""):
    return browse("instrument", mbid, inc)
def browse_label(mbid: str, inc: str = ""):
    return browse("label", mbid, inc)
def browse_place(mbid: str, inc: str = ""):
    return browse("place", mbid, inc)
def browse_recording(mbid: str, inc: str = ""):
    return browse("recording", mbid, inc)
def browse_release(mbid: str, inc: str = ""):
    return browse("release", mbid, inc)
def browse_release_group(mbid: str, inc: str = ""):
    return browse("release-group", mbid, inc)
def browse_series(mbid: str, inc: str = ""):
    return browse("series", mbid, inc)
def browse_work(mbid: str, inc: str = ""):
    return browse("work", mbid, inc)
def browse_url(mbid: str, inc: str = ""):
    return browse("url", mbid, inc)

# ================
# miscellaneous
# ================

def get_size(link) -> str:
    response = requests.head(link)
    size = response.headers['Content-Length']
    return str(size)
    # return str(size/1024*1024)+'mb' if size > 1024*1024 else str(size//1024)+'kb'

def save(link: str, path: str) -> None:
    """
    gets content from link and
    saves the contents to the given path
    """

    response = requests.get(link)
    content = response.content

    with open(path, "wb+") as imgfile:
        imgfile.write(content)
