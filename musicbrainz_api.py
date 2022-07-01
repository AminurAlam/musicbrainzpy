"""
A basic MusicBrainz API wrapper
"""

__version__ = "1.2.0"
__author__ = "AminurAlam"

import json
import requests

mbz_root_url = "https://musicbrainz.org/ws/2"
caa_root_url = "https://coverartarchive.org"


# ===============
# for cover art
# ===============

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
        return {
            "response": response,
            "error": error}

def release_art(mbid: str):
    return caa_req("release", mbid)

def release_group_art(mbid: str):
    return caa_req("release-group", mbid)


# ============
# for lookup
# ============

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
        "inc": inc}
    url = f"{mbz_root_url}/{entity}/{mbid}"
    response = requests.get(url, params=params)

    return json.loads(response.content.decode())

def lookup_artist(mbid: str,
        inc: str = "recordings+releases+release-groups+works"):
    return lookup("artist", mbid, inc)

def lookup_label(mbid: str,
        inc: str = "releases"):
    return lookup("label", mbid, inc)

def lookup_recording(mbid: str,
        inc: str = "artists+releases+isrcs+url-rels"):
    return lookup("recording", mbid, inc)

def lookup_release(mbid: str,
        inc: str = "artists+collections+labels+recordings+release-groups"):
    return lookup("release", mbid, inc)

def lookup_release_group(mbid: str,
        inc: str = "artists+releases"):
    return lookup("release-group", mbid, inc)


# ===============
# for searching
# ===============

def search(entity: str, query: str, limit: int, offset: int):
    """
    search entities to be added:
        area, event, genre, instrument, place, series, work, url
    search documentation:
        https://musicbrainz.org/doc/MusicBrainz_API/Search
    """

    params = {
        "query": query,
        "limit": str(limit),
        "offset": str(offset),
        "fmt": "json"}
    url = f"{mbz_root_url}/{entity}"
    response = requests.get(url, params=params)

    return json.loads(response.content.decode())

def search_artist(query: str, limit: int, offset: int):
    return search("artist", query, limit, offset)

def search_label(query: str, limit: int, offset: int):
    return search("label", query, limit, offset)

def search_recording(query: str, limit: int, offset: int):
    return search("recording", query, limit, offset)

def search_release(query: str, limit: int, offset: int):
    return search("release", query, limit, offset)

def search_release_group(query: str, limit: int, offset: int):
    return search("release-group", query, limit, offset)


# ===============
# misc
# ===============

def get_size(link) -> str:
    return "0"
    # response = requests.head(link)
    # size = response.headers['Content-Length']
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
