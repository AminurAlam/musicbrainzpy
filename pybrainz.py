"""
A basic MusicBrainz API
"""


__version__ = "1.1.0"
__author__ = "AminurAlam"


import json
import requests


def _mbz_req(parameters: dict) -> dict:
    mbz_root_url = "https://musicbrainz.org/ws/2/"
    entity = parameters["entity"]
    cls = parameters["cls"]

    if cls == "Search":
        url = f"{mbz_root_url}{entity}?"
    elif cls == "Lookup":
        url = f"{mbz_root_url}{entity}/{parameters['mbid']}?"
    elif cls == "Browse":
        url = f"{mbz_root_url}{entity}?"
    else:
        url = f"{mbz_root_url}"

    for key, value in parameters.items():
        if key not in ["entity", "cls", "mbid", "discid", "isrc", "iswc"]:
            url += f"{key}={value}&"

    resp = requests.get(url + "fmt=json")

    try:
        return json.loads(resp.content.decode())
    except Exception as error:
        return {
                "url": url + "fmt=json",
                "response": resp,
                "content": resp.content,
                "text": resp.text,
                "error": error,
                }


def _caa_req(entity: str, mbid: str) -> dict:
    """
    307 redirect to an index.json file, if there is a release with this MBID.
    400 if {mbid} cannot be parsed as a valid UUID.
    404 if there is no release with this MBID.
    405 if the request method is not one of GET or HEAD.
    406 if the server is unable to generate a response.
    503 if the user has exceeded their rate limit
    """
    caa_root_url = "https://coverartarchive.org"
    caa_url = f"{caa_root_url}/{entity}/{mbid}"
    resp = requests.get(caa_url)

    try:
        return json.loads(resp.content.decode())
    except Exception as error:
        return {
                "url": caa_url,
                "response": resp,
                "content": resp.content,
                "text": resp.text,
                "error": error,
                }


# ===============
# for cover art
# ===============


def release_art(
        mbid: str):

    return _caa_req("release", mbid)


def release_group_art(
        mbid: str):

    return _caa_req("release-group", mbid)


# ============
# for lookup
# ============


def lookup(
        entity: str,
        mbid: str,
        inc: str):
    """
    lookup entities to be added:
    area, collection, event, genre, instrument, place, series, work, url

    some additional inc= parameters:
    discids, media, isrcs, artist-credits, various-artists

    misc inc= arguments:
    aliases, annotation, tags, ratings, user-tags,
    user-ratings, genres, user-genres
    """

    parameters = {
        "entity": entity,
        "cls": "Lookup",
        "mbid": mbid,
        "inc": inc}

    return _mbz_req(parameters)


def lookup_artist(
        mbid: str,
        inc: str = "recordings+releases+release-groups+works"):

    return lookup("artist", mbid, inc)


def lookup_label(
        mbid: str,
        inc: str = "releases"):

    return lookup("label", mbid, inc)


def lookup_recording(
        mbid: str,
        inc: str = "artists+releases+isrcs+url-rels"):

    return lookup("recording", mbid, inc)


def lookup_release(
        mbid: str,
        inc: str = "artists+collections+labels+recordings+release-groups"):

    return lookup("release", mbid, inc)


def lookup_release_group(
        mbid: str,
        inc: str = "artists+releases"):

    return lookup("release-group", mbid, inc)


# ===============
# for searching
# ===============


def search(
        entity: str,
        query: str,
        limit: int,
        offset: int):
    """
    search entities to be added:
    area, event, genre, instrument, place, series, work, url
    """

    parameters = {
        "entity": entity,
        "cls": "Search",
        "query": query,
        "limit": str(limit),
        "offset": str(offset)}

    return _mbz_req(parameters)


def search_artist(
        query: str,
        limit: int = 15,
        offset: int = 0):

    return search("artist", query, limit, offset)


def search_label(
        query: str,
        limit: int = 15,
        offset: int = 0):

    return search("label", query, limit, offset)


def search_recording(
        query: str,
        limit: int = 15,
        offset: int = 0):

    return search("recording", query, limit, offset)


def search_release(
        query: str,
        limit: int = 30,
        offset: int = 0):

    return search("release", query, limit, offset)


def search_release_group(
        query: str,
        limit: int = 25,
        offset: int = 0):

    return search("release-group", query, limit, offset)


# "7c22ad5e-746f-4a0d-aacc-f668e0383ab6"
