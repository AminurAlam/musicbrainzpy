#Musicbrainz artwork downloader
#start by searching for an album
#it'll get all the results and save the links
#download them by using download.py


import os
import json, requests
import wget, xmltodict


red="\33[31m"
grn="\33[32m"
ylw="\33[33m"
blu="\33[36m"
wht="\33[00m"


#takes links, folder and country
#and downloads artwork to the folder
def artdl(meta,folder,country="NA"):
	for image in meta["images"]:

		try: front = image["front"]
		except: front = "not found"

		try: type = types[0]
		except: type = ["empty"]

		try: link = image["image"]
		except: link = "not found"

		if front == True or type == "Front":
			name = country + link.split("/")[-1]
			path2 = f"files/{folder}/{name}"

			wget.download(link,path2)


#takes mbz links gets the results and converts them to json
def request(searchUrl):
	data = requests.get(searchUrl).content
	metadata = json.loads(json.dumps(xmltodict.parse(data)))
	return metadata


#takes mbid of release and saves results in a file
def get_images(mbid,folder,country):
	base = "https://coverartarchive.org/release/"
	metadata = requests.get(base+mbid).content
	meta = metadata.decode("ascii")

	try: meta = json.loads(meta)
	except: meta = {"images":"empty"}

	if meta["images"] == "empty" : print(f"{red}no images{wht}")
	else: artdl(meta,folder,country)


#takes mbid of release-group and gets mbid of all releases
def lookup_rg(mbid,folder,inc="releases"):
	base = "https://musicbrainz.org/ws/2/release-group/"
	searchUrl = base + f"{mbid}?inc={inc}"
	metadata = request(searchUrl)
	meta = metadata["metadata"]["release-group"]["release-list"]

	#when there is only one release
	if meta["@count"] == 1 :
		release = meta["release"]

		try: date = release["date"]
		except: date = "not found"

		try: country = release["country"]
		except: country = "not found"

		try: id = release["@id"]
		except: id = "not found"

		try: os.mkdir(f"files/{title}/{id}")
		except: print("could not make if folder",id)

		print(f"[{ylw}{country}{wht}]{id} {date}")

		get_images(id,folder)

	#when there are multiple releassles
	else:
		for dic in meta["release"]:

			try: id = dic["@id"]
			except: id = "not found"

			try: title = dic["title"]
			except: title = "not found"

			try: date = dic["date"]
			except: date = red+"0000"+wht

			try: country = dic["country"]
			except: country = red+"NA"+wht

			print(f"\n{country} {date}")

			get_images(id,folder,country)


#takes a query and prints results for it
def search_rg(query,limit=10,offset=0):
	base = "https://musicbrainz.org/ws/2/release-group"
	searchUrl = base + f"?query={query}&limit={limit}"
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

		try: title = dic["title"]
		except: title = "not found"

		try: id = dic["@id"]
		except: id = "not found"

		try: type2 = dic["@type"]
		except: type2 = "not found"

		print(f"""[{ylw}{n}{wht}] [{type2}]
{blu}{artist} - {title}{wht}
""")

	num = int(input(f"{grn}>choose release-group: {wht}"))

	mbid = list[num-1]["@id"]
	title = list[num-1]["title"]

	for illegal in ["/","\\",":","*","?","\"","<",">"]:
		folder = title.replace(illegal,"_")

	try: os.mkdir(f"files/{folder}")
	except: print(f"{red}could not make album directory{wht}")

	#try: os.mkdir(f"files/{folder}/Covers")
	#except: print(f"{red}could not make Covers directory{wht}")

	lookup_rg(mbid,folder)


#main function
#this asks you for query to search for
#type "limit [num]" to change number of results
def main():
	query = input(f"{grn}>enter query: {wht}")

	if query.startswith("limit"):
		limit = int(query.split()[1])
		print(f"limit set to {limit}")
		search_rg(input(f"{grn}>enter query: {wht}"),limit)
	else:
		search_rg(query)

main()
