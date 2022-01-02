









import json
import requests
import xmltodict

def request(searchUrl):
	data = requests.get(searchUrl).content
	metadata = json.loads(json.dumps(xmltodict.parse(data)))
	return metadata


def search_artist(base,entity_type,query,limit=5,offset=0):
	base2 = base + entity_type
	searchUrl = base2 + f"?query={query}&limit={limit}"
	metadata = request(searchUrl)
	list = metadata["metadata"]["artist-list"]["artist"]

	for i in list:
		print(type(i),i)


def search_rg(base,entity_type,query,limit=5,offset=0):
	base2 = base + entity_type
	searchUrl = base2 + f"?query={query}&limit={limit}"
	metadata = request(searchUrl)
	list = metadata["metadata"]["release-group-list"]["release-group"]

	for dic in list:
		print(f"""
	artist : {dic["artist-credit"]["name-credit"]["name"]}
	title : {dic["title"]}
	id : {dic["@id"]}
	type : {dic["@type"]}
	type-id : {dic["@type-id"]}""")



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
2 : release group
3 : lookup
""")
entity_type = int(input("search for: "))

if entity_type == 1: print("starting search for artist")
elif entity_type == 2: search_rg(base,"release-group",query,limit)
else: print("the given value doesnt match")
