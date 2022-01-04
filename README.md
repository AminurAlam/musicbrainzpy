# musicbrainzpy
python wrapper for musicbrainz api

# How to use

STANDALONE:

On running the code it'll ask you which function you want to use
enter the number besides the given function
it'll then ask for query of what you wanna search

IMPORT IT AS A MODULE:

edit musicbrainz.py to remove main() from the last line
put the file in your working directory
import it using
```py
import musicbrainz as mbz
```
and then call the functions
```py
mbz.main()
mbz.search_artist(query,limit,offset)
mbz.lookup_artist(mbid)
mbz.search_rg(query,limit,offset)
mbz.lookup_rg(mbid,inc)
```

# Musicbrainz API

![MusicBrainz](https://staticbrainz.org/MB/header-logo-1f7dc2a.svg)

https://musicbrainz.org/doc/MusicBrainz_API
