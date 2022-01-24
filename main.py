"""
Musicbrainz artwork downloader
start by searching for an album
it'll get all the results and
downloads them one by one
"""

import os
import json, requests
import wget, xmltodict

#info
__version__ = "1.1"
__author__ = "AminurAlam"

#colors
red="\33[31m"
grn="\33[32m"
ylw="\33[33m"
blu="\33[36m"
wht="\33[00m"

#configs
class config:
	make_files_dir = True
	make_region_dir = False

	skip_existing = True
	show_progress = True
	verbose = False

	dl_front = True
	dl_back = False
	dl_booklet = False
	dl_all = False


#takes links, folder and country
#and downloads artwork to the folder
#files/{folder}/{id}.jpg
def artdl(meta,folder,country="NA"):
	for image in meta["images"]:

		try: front = image["front"]
		except: front = "not found"

		try: types = image["types"]
		except: types = ["empty"]

		try: link = image["image"]
		except: link = "not found"

		try: id = image["id"]
		except: id = link.split("/")[-1].replace(".jpg","")

		#only downloads front cover
		#edit this to get back + booklet too
		#Front, Back, Booklet, Obi
		if front == True or "Front" in types:
			name = str(id) + "-" + country + ".jpg"
			path2 = f"files/{folder}/{name}"

			#skips downloading if file exists
			try:
				open(path2)
				print(f"{ylw}skipping...{wht}")

			#downloads file
			except:
				print(f"{types} {blu}{link}{wht}")
				wget.download(link,path2)

			print("\n")


#takes mbz links gets the results
#converts the xml result to json
def request(searchUrl):
	response = requests.get(searchUrl)
	if config.verbose is True: print(f"status: {response}")
	data = response.content
	metadata = json.loads(json.dumps(xmltodict.parse(data)))
	return metadata


#making logs of error to find bugs
def log_errors(mbid,meta,folder):
	#ERRORS are saves in a file to be checked
	with open(f"files/{folder} {mbid}.txt","w+") as errfile:
		errfile.write(str(meta))

	traceback.print_stack()


#takes mbid of release and saves results in a file
def get_images(mbid,folder,country):
	base = "https://coverartarchive.org/release/"
	rgUrl = base + mbid
	metadata = requests.get(rgUrl).content
	meta = metadata.decode()

	#tries to load links and download them
	try:
		meta = json.loads(meta)
		artdl(meta,folder,country)

	#prints this if no images were found
	except Exception as e:
		print(f"{red}no images{wht}\n")

		if config.verbose is True:
			print(f"rg url: {rgUrl}")
			log_errors(mbid,meta,folder)


#takes mbid of release-group and gets mbid of all releases
def lookup_rg(mbid,folder,inc="releases"):
	base = "https://musicbrainz.org/ws/2/release-group/"
	searchUrl = base + f"{mbid}?inc={inc}"
	metadata = request(searchUrl)
	meta = metadata["metadata"]["release-group"]["release-list"]

	if config.verbose is True:
		print("writing rg meta to a file")
		with open(f"files/ERR {folder}.txt","w+") as dicfile:
			dicfile.write(str(meta))

	#getting items from the release
	def get_items(dic):
		try: id = dic["@id"]
		except: id = "not found"

		try: title = dic["title"]
		except: title = "not found"

		try: date = dic["date"]
		except: date = red+"0000"+wht

		try: country = dic["country"]
		except: country = red+"NA"+wht

		print(f"[{ylw}{country}{wht}] {id} [{date}]")

		get_images(id,folder,country)

	#when there is only one release
	if meta["@count"] == "1" : get_items(meta["release"])

	#when there are multiple releassles
	else:
		for dic in meta["release"]: get_items(dic)


#takes a query and prints results for it
#you can change the number of results shown here
def search_rg(query,limit=5,offset=0):
	base = "https://musicbrainz.org/ws/2/release-group"
	searchUrl = base + f"?query={query}&limit={limit}"
	metadata = request(searchUrl)
	list = metadata["metadata"]["release-group-list"]["release-group"]

	n = 0
	for dic in list:
		n += 1
		und = dic["artist-credit"]["name-credit"]

		#when there is one artist
		if type(und) == type({}):
			artist = und["name"]
		#when there are multiple artists
		elif type(und) == type([]):
			artist = ""
			for undic in und:
				artist = artist + undic["name"] + ", "
			artist = artist[:-2]
		#when there is no artist
		else:
			artist = "not found"

		try: title = dic["title"]
		except: title = "not found"

		try: id = dic["@id"]
		except: id = "not found"

		try: type2 = dic["@type"]
		except: type2 = "not found"

		print(f"[{ylw}{n}{wht}] [{type2}] {id}")
		print(f"{blu}{artist} - {title}{wht}\n")

	num = int(input(f"{grn}>choose release-group: {wht}"))

	if num == 0:
		print(f"{red}exiting...{wht}")
		exit()

	mbid = list[num-1]["@id"]
	title = list[num-1]["title"]

	for illegal in ["/","\\",":","*","?","\"","<",">"]:
		folder = title.replace(illegal,"_")

	if config.make_files_dir is True:
		try: os.mkdir(f"files")
		except: None

	if config.verbose is True:
		print(f"\n{grn}download started{wht}")

		try: os.mkdir(f"files/{folder}")
		except: print(f"{red}could not make album directory{wht}")

		print(f"starting lookup_rg with")
		print(f"  mbid: {mbid}\n  folder: {folder}")
	else:
		try: os.mkdir(f"files/{folder}")
		except: None

	lookup_rg(mbid,folder)


#main function
#this asks you for query to search for
#type "limit [num]" to change number of results
def main():
	query = input(f"{grn}>enter query: {wht}")

	if query in ["Exit","exit"]:
		print(f"{red}exiting...{wht}")
		exit()
	elif query.startswith("limit"):
		limit = int(query.split()[1])
		print(f"limit set to {limit}")
		search_rg(input(f"{grn}>enter query: {wht}"),limit)
	else:
		search_rg(query)


if __name__ == '__main__':
	main()
