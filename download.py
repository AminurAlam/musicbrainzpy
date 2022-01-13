<<<<<<< HEAD

=======
import os, json, wget

red="\33[31m"
grn="\33[32m"
ylw="\33[33m"
blu="\33[36m"
wht="\33[00m"




path = "files/"

def wdl(link,path2):

	path3 = "/".join([
	"files",path2.split("/")[1],
	"Covers",link.split("/")[-1]])

	wget.download(link,path3)


def artdl(path2,meta):

	for image in meta["images"]:

		try: types = image["types"]
		except: types = [ ]

		try: front = image["front"]
		except: front = "not found"

		try: back = image["back"]
		except: back = "not found"

		try: edit = image["edit"]
		except: edit = "not found"

		try: link = image["image"]
		except: link = "not found"

		try: comment = image["comment"]
		except: comment = "no comment"

		try: approved = image["approved"]
		except: approved = "not found"

		try: id = image["id"]
		except: id = "not found"

		try: thumbs = image["thumbnails"]
		except: thumbs = {"empty":"empty"}

		try: type = types[0]
		except: type = ["empty"]

		if front == True or type == "Front":
			#print(front,type)
			#print(f"{blu}{link}{wht}\n")
			wdl(link,path2)


def getlink(rgfolder):

	releaselist =  os.listdir(f"files/{rgfolder}/")

	try: os.mkdir(path+rgfolder+"/Covers")
	except: None

	try: releaselist.remove("Covers")
	except: None

	for release in releaselist:
		path2 = "/".join(["files",rgfolder,release])

		with open(f"{path2}/meta.txt","r") as file:
			text = file.read()

			try: meta = json.loads(text)
			except: meta = {"images":"empty"}

			if meta["images"] == "empty" : None
			else: artdl(path2,meta)


def picker():
	rglist = [ ]

	for rg in os.listdir(path):
		if os.path.isdir(path + rg):
			rglist.append(rg)

	rglist.sort()
	rglist.insert(0,"exit")

	for rg in rglist:
		print (f"{rglist.index(rg)} : {rg}")

	id = int(input(">select: "))
	return rglist[id]

def main():
	rgfolder = picker()
	getlink(rgfolder)
main()
>>>>>>> 94126c1 (download.py is made)
