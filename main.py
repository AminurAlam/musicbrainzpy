try: import os, json, requests, xmltodict
except: print("""packages missing, install them by:
pip install [package_name]

packages reqiired: json, requests, xmltodict""")

red="\33[31m"
grn="\33[32m"
ylw="\33[33m"
blu="\33[36m"
wht="\33[00m"


def request(searchUrl):
	data = requests.get(searchUrl).content
	metadata = json.loads(json.dumps(xmltodict.parse(data)))
	return metadata

def get_images(mbid,title):
	base = "https://coverartarchive.org/release/"
	metadata = requests.get(base + mbid).content
	meta = metadata.decode("ascii")

	with open(f"files/{title}/{mbid}/meta.txt","w+") as file:
		file.write(meta)


def lookup_rg(mbid,title,inc="releases"):
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

#when there are multiple releassles
	else:
		for dic in meta["release"]:

			try: id = dic["@id"]
			except: id = "not found"

			try: title = dic["title"]
			except: title = "not found"

			try: date = dic["date"]
			except: date = red+"0000"

			try: country = dic["country"]
			except: country = red+"NA"

			try: os.mkdir(f"files/{title}/{id}")
			except: print("failed to make id folder",id)

			print(f"[{ylw}{country}{wht}] {id} {date}{wht}")

			get_images(id,title)


def search_rg(query,limit=5,offset=0):
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

		print(f"""
[{ylw}{n}{wht}] [{type2}] {id}
{artist} - {title}""")

	num = int(input("\n>choose release-group: "))

	mbid = list[num-1]["@id"]
	title = list[num-1]["title"]

	for illegal in ["/","\\",":","*","?","\"","<",">"]:
		title = title.replace(illegal,"_")

	try: os.mkdir(f"files/{title}")
	except: print("could not make album directory")

	lookup_rg(mbid,title)


def main():
	# area, artist, event, genre, instrument, label, place
	#recording, release, release-group, series, work, url
	print("""
0 : exit
1 : release-group
2 : lookup release-group
""")

	entity_type = int(input("search for: "))

	#asks for what you want to look for
	query = input(">search query: ")

	if entity_type == 0 : exit()

	elif entity_type == 1: search_rg(query)
	elif entity_type == 2: lookup_rg(query)

	else: print("the given value doesnt match")


search_rg(input(">enter query: "))

