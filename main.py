









import json
import requests
import xmltodict

def request(searchUrl):
	data = requests.get(searchUrl).content
	metadata = json.loads(json.dumps(xmltodict.parse(data)))
	return metadata

def search_artist(base,entity_type,query,limit=5,offset=0):
	base2 = base + entity_type
	searchUrl = base2 + f"?query={query}&limit={limit}" #&offset={offset}"
	metadata = request(searchUrl)
	list = metadata["metadata"]["artist-list"]["artist"]
	print("type",type(list))
	print("lenth",len(list))
	print()
	for i in list:
		print(type(i),i)

#The API root URL
base = "https://musicbrainz.org/ws/2/"

# area, artist, event, genre, instrument, label, place
#recording, release, release-group, series, work, url
entity_type = "artist"
limit = 2
#asks for what you want to look for
query = "Carly Rae Jepsen" #input(">search query")

search_artist(base,entity_type,query,limit)
