import json
import requests
import xmltodict

def request(searchUrl):
	data = requests.get(searchUrl).content
	metadata = json.loads(json.dumps(xmltodict.parse(data)))
	return metadata


def search_artist(query,limit=5,offset=0):
	base2 = "https://musicbrainz.org/ws/2/artist"
	searchUrl = base2 + f"?query={query}&limit={limit}"
	metadata = request(searchUrl)
	list = metadata["metadata"]["artist-list"]["artist"]

	for i in list:
		print(type(i),i)


def lookup_rg(mbid,inc="releases"):
        base2 = "https://musicbrainz.org/ws/2/release-group/"
        searchUrl = base2 + f"{mbid}?inc={inc}"
        metadata = request(searchUrl)
        list = metadata["metadata"]["release-group"]["release-list"]
        for dic in list:
                print("""
id      : {dic["@id"]}
title   : {dic["title"]}
date    : {dic["date"]}
country : {dic["country"]}
barcode : {dic["barcode"]}""")


def search_rg(query,limit=5,offset=0):
	base2 = "https://musicbrainz.org/ws/2/release-group"
	searchUrl = base2 + f"?query={query}&limit={limit}"
	metadata = request(searchUrl)
	list = metadata["metadata"]["release-group-list"]["release-group"]

	n = 0
	for dic in list:
		n += 1
		print(f"""{n}
artist : {dic["artist-credit"]["name-credit"]["name"]}
title  : {dic["title"]}
id     : {dic["@id"]}
type   : {dic["@type"]}""")

	num = int(input(">choose release-group: "))
	mbid = list[num-1]["@id"]
	lookup_rg(mbid)


#The API root URL
base = "https://musicbrainz.org/ws/2/"

#limit of results you want to see
limit = 5

#asks for what you want to look for
query = input(">search query: ")

# area, artist, event, genre, instrument, label, place
#recording, release, release-group, series, work, url
print("""
1 : artist
2 : release-group
3 : lookup release-group
4 :""")


entity_type = int(input("search for: "))

if entity_type == 1: search_artist(query,limit)
elif entity_type == 2: search_rg(query,limit)
elif entity_type == 3: lookup_rg(query)
else: print("the given value doesnt match")
