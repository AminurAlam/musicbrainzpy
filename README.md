# MusicbrainzPy
MusicBrainz artwork downloader written in python


# Requirements
Python v3.11.0 or above
```sh
pip install requests
```


# How to use
1. clone the repository
```sh
git clone --depth 1 "https://github.com/AminurAlam/musicbrainzpy.git"
```
2. run cover_art.py using python:
```sh
python3 cover_art.py "search query"
```
3. it'll show a few results
4. enter the number next to the result to select it
5. it'll then go through all the albums and download them in `Covers/{Artist} - {Album}/filename.jpg`


# Help text

```
usage:
cover_art.py query [-l NUM] [-a] [-d] [-o PATH] [-fi TYPE] [-fs TYPE]

options:
  -h, --help                      show this help message and exit
  -l NUM, --limit NUM             max number of results displayed
  -a, --auto-select               automatically pick the best search result
  -v, --version                   show version and exit
  -n, --dry-run                   run without downloading artwork
  -d, --disable-color             removes colors
  -o PATH, --outdir PATH          change the output directory
  -fi TYPE, --filter-image TYPE   filter images
  -fs TYPE, --filter-search TYPE  filter search results
```


# Documentation

https://musicbrainz.org/doc/MusicBrainz_API

https://musicbrainz.org/doc/Cover_Art_Archive/API
