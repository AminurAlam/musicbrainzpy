"""
A basic MusicBrainz and Internet Archive API wrapper
"""

__version__ = "1.4.1"
__author__ = "AminurAlam"

import json
import requests

mbz_root_url = "https://musicbrainz.org/ws/2"
caa_root_url = "https://coverartarchive.org"
ia_root_url = "https://archive.org/download"
mxm_root_url = "https://api.musixmatch.com/ws/1.1"


# =============
# musixmatch
# =============
def mxm_req(method: str, params: dict):
    """
    Metadata:
        Track     Track Rating, Instrumental and Explicit flags, Favourites, Music Genre, Song titles translations, Track Id (track_id, commontrack_id)
        Artist    Comments and country, Artist translations, Artist rating, Artist music genre
        Album     Album Rating, Album type and release date, Album copyright and label (Label, Copyright), Album music genre (Primary genere, Secondary genre)

    Input Parameters:
        Authentication   apikey
        Objects          track_id, artist_id, album_id, commontrack_id, track_mbid, artist_mbid, album_mbid
        Querying         q_track, q_artist, q_lyrics, q
        Filtering        f_has_lyrics, f_is_instrumental, f_has_subtitle, f_music_genre_id, f_subtitle_length, f_subtitle_length_max_deviation, f_lyrics_language, f_artist_id, f_artist_mbid
        Grouping         g_commontrack
        Sorting          s_track_rating, s_track_release_date, s_artist_rating
        Result Page      page, page_size
        Output Format    subtitle_format
        Localization     country

    Api Methods:
        chart.artists.get
        chart.tracks.get
        track.search
        track.get
        track.lyrics.get
        track.lyrics.post
        track.lyrics.mood.get
        track.snippet.get
        track.subtitle.get
        track.richsync.get
        track.lyrics.translation.get
        track.subtitle.translation.get
        music.genres.get
        matcher.lyrics.get
        matcher.track.get
        matcher.subtitle.get
        artist.get
        artist.search
        artist.albums.get
        artist.related.get
        album.get
        album.tracks.get
        tracking.url.get
        catalogue.dump.get
        work.post

    Status codes:
        200    The request was successful.
        400    The request had bad syntax or was inherently impossible to be satisfied.
        401    Authentication failed, probably because of invalid/missing API key.
        402    The usage limit has been reached, either you exceeded per day requests limits or your balance is insufficient.
        403    You are not authorized to perform this operation.
        404    The requested resource was not found.
        405    The requested method was not found.
        500    Ops. Something were wrong.
        503    Our system is a bit busy at the moment and your request can’t be satisfied.
    """
    response = requests.get(f"{mxm_root_url}/{method}", params=params)

    return json.loads(response.content.decode()) if response.status_code == 200 else {}


# ==================
# archive.org api
# ==================
def ia_req(mbid: str) -> dict:
    response = requests.get(f"{ia_root_url}/mbid-{mbid}/index.json")

    # return {} if response.status_code == 404 else json.loads(response.content.decode())
    return json.loads(response.content.decode()) if response.status_code == 200 else {}


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
def lookup(entity: str, mbid: str, inc: str = '') -> dict:
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
def save(link: str, path: str, allowed) -> tuple[bool, str, str]:
    """
    downloads 'link' if its size is between min and max
    """

    try:
        img_link: str = requests.head(link).headers['Location']
        head = requests.head(img_link).headers
    except Exception as e:
        print(f"error while requesting: {e}")
        exit()
    size: int = int(head['Content-Length'])
    ft: str = head['Content-Type'].split('/')[-1]
    human_size: str = f"{round(size/1_000_000, 2)} mb" if 1_000_000 < size else f"{size//1_000} kb"

    if allowed.dry or \
    (not allowed.pdf and ft == "pdf") or \
    not (allowed.size[0]*1000 < size < allowed.size[1]*1000):
        return False, human_size, ft

    try:
        with open(path, "wb+") as imgfile:
            imgfile.write(requests.get(img_link).content)
    except Exception as e:
        print(f"error while requesting: {e}")
        exit()

    return True, human_size, ft
