
# MusicbrainzPy
MusicBrainz artwork downloader written in python


# How to use
1. clone the repository
2. run cover_art.py using python:
```bash
python3 cover_art.py "search query"
```
3. it'll show a few results
4. enter the number next to the result to select it
5. it'll then go through all the albums and download them in `Covers/{Artist} - {Album}/filename.jpg`


# help text

```
usage:
  python3 cover_art.py query [-l NUM] [-sf TYPE] [-f TYPE] [-o PATH]

options:
  -h, --help                      show this help message and exit
  -l NUM, --limit NUM             max number of results displayed
  -a, --auto-select               automatically pick the best search result
  -v, --verbose                   change logging level to debug
  -V, --version                   show version and exit
  -n, --dry-run                   run without downloading artwork
  -d, --disable-color             removes colors
  -o PATH, --outdir PATH          change the output directory
  -fi TYPE, --filter-image TYPE   filter images
  -fs TYPE, --filter-search TYPE  filter search results
```

# docs

![MusicBrainz](https://staticbrainz.org/MB/header-logo-1f7dc2a.svg)

https://musicbrainz.org/doc/MusicBrainz_API

![CoverArtArchive](https://coverartarchive.org/img/navbar_logo.svg)

https://musicbrainz.org/doc/Cover_Art_Archive/API
