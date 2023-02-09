"""
A basic MusicBrainz and Internet Archive API wrapper
"""

__version__ = "1.4.0"
__author__ = "AminurAlam"

import json
import requests

mbz_root_url = "https://musicbrainz.org/ws/2"
caa_root_url = "https://coverartarchive.org"
ia_root_url = "https://archive.org/download"


# ==================
# archive.org api
# ==================

def ia_req(mbid: str) -> dict:
    response = requests.get(f"{ia_root_url}/mbid-{mbid}/index.json")

    return {} if response.status_code == 404 else json.loads(response.content.decode())


# ====================
# cover art archive
# ====================

def caa_req(entity: str, mbid: str) -> dict:
    """
    there are 2 types of 'entities':
        release, release-group

    accepted methods:
        GET, HEAD

    common status codes:
        307    redirect to an index.json file, if there is a release with this MBID.
        400    if {mbid} cannot be parsed as a valid UUID.
        404    if there is no release with this MBID.
        405    if the request method is not one of GET or HEAD.
        406    if the server is unable to generate a response.
        503    if the user has exceeded their rate limit
    """
    response = requests.get(f"{caa_root_url}/{entity}/{mbid}")

    return {} if response.status_code == 404 else json.loads(response.content.decode())


# ============
# searching
# ============

def search(entity: str, query: str, limit: int, offset: int) -> dict:
    """
    there are 13 types of 'entities':
        area, artist, event, genre, instrument, label, place,
        recording, release, release-group, series, work, url

    these are 3 non-core 'entities':
        rating, tag, collection
    """
    response = requests.get(f"{mbz_root_url}/{entity}", params={
        "query": query,
        "limit": str(limit),
        "offset": str(offset),
        "fmt": "json"
    })

    return {} if response.status_code == 404 else json.loads(response.content.decode())


# =========
# browse
# =========

def browse(entity: str, link: str, mbid: str, limit: int = 25, offset: int = 25) -> dict:
    """
    'entities' and their available 'links':
        area              collection
        artist            area, collection, recording, release, release-group, work
        collection        area, artist, editor, event, label, place, recording, release, release-group, work
        event             area, artist, collection, place
        instrument        collection
        label             area, collection, release
        place             area, collection
        recording         artist, collection, release, work
        release           area, artist, collection, label, track, track_artist, recording, release-group
        release-group     artist, collection, release
        series            collection
        work              artist, collection
        url               resource
    """
    response = requests.get(f"{mbz_root_url}/{entity}", params={
        link: mbid,
        "limit": limit,
        "offset": offset,
        "fmt": "json"
    })

    return {} if response.status_code == 404 else json.loads(response.content.decode())


# =========
# lookup
# =========

def lookup(entity: str, inc: str, mbid: str) -> dict:
    """
    'entities' and their 'inc' parameters:
        area
        artist            recordings, releases, release-groups, works
        collection        user-collections (includes private collections, requires authentication)
        event
        genre
        instrument
        label             releases
        place
        recording         artists, releases, isrcs, url-rels
        release           artists, collections, labels, recordings, release-groups
        release-group     artists, releases
        series
        work
        url

    some additional 'inc' parameters:
        discids, media, isrcs, artist-credits, various-artists

    misc 'inc' arguments:
        aliases, annotation, tags, ratings, user-tags, user-ratings, genres, user-genres
    """
    response = requests.get(f"{mbz_root_url}/{entity}/{mbid}", params={
        "inc": inc,
        "fmt": "json"
    })

    return {} if response.status_code == 404 else json.loads(response.content.decode())


# ================
# miscellaneous
# ================

def save(link: str, path: str, length: int) -> int:
    """
    downloads 'links' if their size is larger than 'length'
    """

    img_link: str = requests.head(link).headers['Location']

    if length != 0 and int(requests.head(img_link).headers['Content-Length']) < length*1000:
        return 0

    response = requests.get(img_link)

    with open(path, "wb+") as imgfile:
        imgfile.write(response.content)

    return int(response.headers['Content-Length'])
