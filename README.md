# MusicbrainzPy

MusicBrainz artwork downloader written in python


# Requirements

Python v3.11.0 or above

```sh
pip install requests
```


# How to use

1. clone the repository and install it


```sh
git clone --depth 1 "https://github.com/AminurAlam/musicbrainzpy.git"
pip install requests musicbrainzpy/
```

2. run cover_art.py using python:


```sh
ca "search query"
```

3. it'll show a few results

4. enter the number next to the result to select it

5. it'll then go through all the albums and download them in `Covers/{Artist} - {Album}/filename.jpg`


# Help text

```
usage:
  cover_art.py <query> [-l NUM] [-o PATH] [-i TYPE] [-s TYPE] [-b MIN_SIZE] [-B MAX_SIZE] [-p] [-n]

options:
  -h, --help                     show this help message and exit
  -l NUM, --limit NUM            limit the number of results displayed
  -o PATH, --outdir PATH         change the output directory where files are saved
  -i TYPE, --filter-image TYPE   filter the type of images saved
  -s TYPE, --filter-search TYPE  filter search results
  -b SIZE, --min-size SIZE       minimum filesize allowed (in kb)
  -B SIZE, --max-size SIZE       maximum filesize allowed (in kb)
  -p, --allow-pdf                download pdf artwork if available
  -n, --dry-run                  dont download anything
```


# Documentation

https://musicbrainz.org/doc/MusicBrainz_API

https://musicbrainz.org/doc/Cover_Art_Archive/API
