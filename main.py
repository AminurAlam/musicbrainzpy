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
	meta = metadata["metadata"]["release-group"]["release-list"]

	if meta["@count"] == 1 :
		release = meta["release"]

		try: date = release["date"]
		except: date = "not found"
		try: country = release["country"]
		except: country = "not found"

		print(f"""
id      : {release["@id"]}
title   : {release["title"]}
date    : {date}
country : {country}
""")

	else:
		for dic in meta["release"]:
			print(f"""
id      : {dic["@id"]}
title   : {dic["title"]}
date    : {dic["date"]}
country : {dic["country"]}""")


def search_rg(query,limit=5,offset=0):
	base2 = "https://musicbrainz.org/ws/2/release-group"
	searchUrl = base2 + f"?query={query}&limit={limit}"
	metadata = request(searchUrl)
	list = metadata["metadata"]["release-group-list"]["release-group"]

	n = 0
	for dic in list:
		n += 1
		und = dic["artist-credit"]["name-credit"]
		if type(und) == type({}):
			artist = und["name"]
		elif type(und) == type([]):
			artist = ""
			for undic in und:
				artist = artist + undic["name"] + ", "
			artist = artist[:-2]

		print(f"""
 {n}
artist : {artist}
title  : {dic["title"]}
id     : {dic["@id"]}
type   : {dic["@type"]}""")

	num = int(input("\n>choose release-group: "))
	try:
		mbid = list[num-1]["@id"]
		lookup_rg(mbid)
	except:
		print("error occured, probably due to wrong entry")




def main():
	# area, artist, event, genre, instrument, label, place
	#recording, release, release-group, series, work, url
	print("""
0 : exit

1 : artist
2 : lookup artist

3 : release-group
4 : lookup release-group
""")

	entity_type = int(input("search for: "))

	#asks for what you want to look for
	query = input(">search query: ")

	if entity_type == 0 : exit()

	elif entity_type == 1: search_artist(query)
	elif entity_type == 2: None

	elif entity_type == 3: search_rg(query)
	elif entity_type == 4: lookup_rg(query)

	else: print("the given value doesnt match")

main()
