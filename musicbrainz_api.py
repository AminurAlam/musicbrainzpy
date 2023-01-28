"""
A basic MusicBrainz API wrapper
"""

__version__ = "1.3.0"
__author__ = "AminurAlam"

import json
import requests

mbz_root_url = "https://musicbrainz.org/ws/2"
caa_root_url = "https://coverartarchive.org"
ia_root_url = "https://archive.org/download"


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
    response = requests.get(f"{caa_root_url}/{entity}/{mbid}")

    if response.status_code == 404:
        return {}

    return json.loads(response.content.decode())


def release_art(mbid: str):
    return caa_req("release", mbid)
def release_group_art(mbid: str):
    return caa_req("release-group", mbid)


# ==================
# archive.org api
# ==================

def ia_req(mbid: str):
    response = requests.get(f"{ia_root_url}/mbid-{mbid}/index.json")

    if response.status_code == 404:
        return {}

    return json.loads(response.content.decode())


# ============
# searching
# ============

def search(entity: str, query: str, limit: int, offset: int) -> dict:
    """
    there are 13 resources which represent core entities:
        area, artist, event, genre, instrument, label, place, recording, release, release-group, series, work, url
    these are non-core resources:
        rating, tag, collection
    search documentation:
        https://musicbrainz.org/doc/MusicBrainz_API/Search
    search query:
        /<ENTITY_TYPE>?query=<QUERY>&limit=<LIMIT>&offset=<OFFSET>
    """
    response = requests.get(
        f"{mbz_root_url}/{entity}",
        params={
            "query": query,
            "limit": str(limit),
            "offset": str(offset),
            "fmt": "json"
        }
    )

    return json.loads(response.content.decode())


def search_area(query: str, limit: int, offset: int): return search("area", query, limit, offset)
def search_artist(query: str, limit: int, offset: int): return search("artist", query, limit, offset)
def search_event(query: str, limit: int, offset: int): return search("event", query, limit, offset)
def search_genre(query: str, limit: int, offset: int): return search("genre", query, limit, offset)
def search_instrument(query: str, limit: int, offset: int): return search("instrument", query, limit, offset)
def search_label(query: str, limit: int, offset: int): return search("label", query, limit, offset)
def search_place(query: str, limit: int, offset: int): return search("place", query, limit, offset)
def search_recording(query: str, limit: int, offset: int): return search("recording", query, limit, offset)
def search_release(query: str, limit: int, offset: int): return search("release", query, limit, offset)
def search_release_group(query: str, limit: int, offset: int): return search("release-group", query, limit, offset)
def search_series(query: str, limit: int, offset: int): return search("series", query, limit, offset)
def search_work(query: str, limit: int, offset: int): return search("work", query, limit, offset)
def search_url(query: str, limit: int, offset: int): return search("url", query, limit, offset)

def search_collection(query: str, limit: int, offset: int): return search("collection", query, limit, offset)
def search_rating(query: str, limit: int, offset: int): return search("rating", query, limit, offset)
def search_tag(query: str, limit: int, offset: int): return search("tag", query, limit, offset)


# =========
# lookup
# =========

def lookup(entity: str, mbid: str, inc: str):
    """
    some additional 'inc=' parameters:
        discids, media, isrcs, artist-credits, various-artists
    misc 'inc=' arguments:
        aliases, annotation, tags, ratings, user-tags, user-ratings, genres, user-genres
    """
    response = requests.get(
        f"{mbz_root_url}/{entity}/{mbid}",
        params={"inc": inc, "fmt": "json"})

    return json.loads(response.content.decode())


def lookup_area(mbid: str, inc: str = ""): return lookup("area", mbid, inc)
def lookup_artist(mbid: str, inc: str = "recordings+releases+release-groups+works"): return lookup("artist", mbid, inc)
def lookup_collection(mbid: str, inc: str = "user-collections"): return lookup("collection", mbid, inc)
def lookup_event(mbid: str, inc: str = ""): return lookup("event", mbid, inc)
def lookup_genre(mbid: str, inc: str = ""): return lookup("genre", mbid, inc)
def lookup_instrument(mbid: str, inc: str = ""): return lookup("instrument", mbid, inc)
def lookup_label(mbid: str, inc: str = "releases"): return lookup("label", mbid, inc)
def lookup_place(mbid: str, inc: str = ""): return lookup("place", mbid, inc)
def lookup_recording(mbid: str, inc: str = "artists+releases+isrcs+url-rels"): return lookup("recording", mbid, inc)
def lookup_release(mbid: str, inc: str = "artists+collections+labels+recordings+release-groups"): return lookup("release", mbid, inc)
def lookup_release_group(mbid: str, inc: str = "artists+releases"): return lookup("release-group", mbid, inc)
def lookup_series(mbid: str, inc: str = ""): return lookup("series", mbid, inc)
def lookup_work(mbid: str, inc: str = ""): return lookup("work", mbid, inc)
def lookup_url(mbid: str, inc: str = ""): return lookup("url", mbid, inc)

def lookup_discid(id: str, inc: str = ""): return lookup("discid", id, inc)
def lookup_isrc(id: str, inc: str = ""): return lookup("isrc", id, inc)
def lookup_iswc(id: str, inc: str = ""): return lookup("iswc", id, inc)


# =========
# browse
# =========

def browse(entity: str, link: str, mbid: str):
    """
    docstring
    """
    response = requests.get(
        f"{mbz_root_url}/{entity}",
        params={link: mbid, "fmt": "json"})

    return json.loads(response.content.decode())


def browse_area(link: str, mbid: str): return browse("area", link, mbid)
def browse_artist(link: str, mbid: str): return browse("artist", link, mbid)
def browse_collection(link: str, mbid: str): return browse("collection", link, mbid)
def browse_event(link: str, mbid: str): return browse("event", link, mbid)
# def browse_genre(link: str, mbid: str): return browse("genre", link, mbid)
def browse_instrument(link: str, mbid: str): return browse("instrument", link, mbid)
def browse_label(link: str, mbid: str): return browse("label", link, mbid)
def browse_place(link: str, mbid: str): return browse("place", link, mbid)
def browse_recording(link: str, mbid: str): return browse("recording", link, mbid)
def browse_release(link: str, mbid: str): return browse("release", link, mbid)
def browse_release_group(link: str, mbid: str): return browse("release-group", link, mbid)
def browse_series(link: str, mbid: str): return browse("series", link, mbid)
def browse_work(link: str, mbid: str): return browse("work", link, mbid)
def browse_url(link: str, mbid: str): return browse("url", link, mbid)


# ================
# miscellaneous
# ================

def save(link: str, path: str, length: int) -> int:
    """
    gets link of the image
    checks if the image is of proper size
    then downloads it
    """

    img_link: str = requests.head(link).headers['Location']

    if length != 0 and int(requests.head(img_link).headers['Content-Length']) < length*1000:
        print("checking\n")
        return 0

    response = requests.get(img_link)
    with open(path, "wb+") as imgfile:
        imgfile.write(response.content)
    return int(response.headers['Content-Length'])
