
# MusicbrainzPy
MusicBrainz artwork downloader written in python


# How to use
1. clone the repository
2. run the file using python:
```bash
python3 cover_art.py "search term" [-h] [-v] [-a]
```
3. it'll show a few results
4. enter the number next to the result to select it
5. it'll then go through all the albums and download them in `Covers/{Album}/filename.jpg`


# help text

```
positional arguments:
  query                 search for an albums

options:
  -h, --help            show this help message and exit
  -l NUM, --limit NUM   number of results shown
  -a, --async           download all covers at once
  -rd, --re-download    re-downloads existing files
  -v, --verbose         change logging level to debug
  -V, --version         show version and exit
```


# API used

![MusicBrainz](https://staticbrainz.org/MB/header-logo-1f7dc2a.svg)

https://musicbrainz.org/doc/MusicBrainz_API

![CoverArtArchive](https://coverartarchive.org/img/navbar_logo.svg)

https://musicbrainz.org/doc/Cover_Art_Archive/API
