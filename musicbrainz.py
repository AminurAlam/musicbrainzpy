#!/usr/bin/env python3

"""
Musicbrainz artwork downloader
start by searching for an album
it'll get all the results and
downloads them one by one

https://musicbrainz.org/doc/MusicBrainz_API
https://musicbrainz.org/doc/Cover_Art_Archive/API
"""

import os
import wget, json, requests, argparse

#info
__version__ = "1.3"
__author__ = "AminurAlam"

#colors
red="\33[31m"
grn="\33[32m"
ylw="\33[33m"
blu="\33[36m"
wht="\33[00m"

#configs
#you can change default configs here
#or pass arguments to change them everytime
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

    limit = "5"


#takes a list and returns joined string
#this solves compatiblity with windows
def get_dir(list):
    if os.name == "nt": path = "\\".join(list)
    else: path = "/".join(list)

    if config.verbose: print(f"for {os.name}, joined path {path}")

    return path


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
        except: id = link.split("/")[-1].split(".")[0]

        #only downloads front cover
        #edit this to get back + booklet too
        #Front, Back, Booklet, Obi
        if front == True or "Front" in types:
            name = f"{str(id)}-{country}.{link.split('.')[-1]}"
            path2 = f"files/{folder}/{name}"

            #skips downloading if file exists
            try:
                open(path2)
                print(f"{ylw}skipping...{wht}",end="")

            #downloads file
            except:
                print(f"{types} {path2}{wht}")
                wget.download(link,path2)

            print("\n")

    print("we are finished downloading.")


#takes mbz links gets the results
def request(head):
    base = "https://musicbrainz.org/ws/2/release-group"
    url = base + head
    resp = requests.get(url)
    content = resp.content.decode()
    content = json.loads(content)

    if config.verbose:
        code = str(resp.status_code)
        print(f"url: {url}")
        print(f"status: {code}")

        with open(f"files/content.txt","w+") as file:
            file.write(str(content))

    return content


#takes mbid of release and saves results in a file
def get_images(mbid,folder,country):
    base = "https://coverartarchive.org/release/"
    url = base + mbid
    resp = requests.get(url)
    content = resp.content.decode()

    #tries to load links and download them
    try:
        content = json.loads(content)
        artdl(content,folder,country)

    #prints this if no images were found
    except Exception as e:
        print(f"{red}no images{wht}\n")

        if config.verbose:
            print(f"rg url: {url}")
            print(f"status: {resp.status_code}")
            print(f"{ylw}{content}{wht}")
            print(f"exception: {red}{e}{wht}")


#takes mbid of release-group and gets mbid of all releases
def lookup_rg(mbid,folder):
    content = request(f"/{mbid}?fmt=json&inc=releases")

    for dic in content["releases"]:
        try: id = dic["id"]
        except: id = "not found"

        try: date = dic["date"]
        except: date = red+"0000"+wht

        try: country = dic["country"]
        except: country = red+"NA"+wht

        print(f"[{ylw}{country}{wht}] {id} [{date}]")
        get_images(id,folder,country)


#takes a query and prints results for it
#you can change the number of results shown here
def search_rg(query,limit="5"):
    content = request(f"?query={query}&limit={limit}&fmt=json")

    n = 0
    for dic in content["release-groups"]:
        n += 1

        try: artist = dic["artist-credit"][0]["name"]
        except: artist = "not found"

        try: title = dic["title"]
        except: title = "not found"

        try: id = dic["id"]
        except: id = "not found"

        try: ptype = dic["primary-type"]
        except: ptype = "not found"

        print(f"[{ylw}{n}{wht}] [{ptype}] {id}")
        print(f"{blu}{artist} - {title}{wht}\n")

    num = int(input(f"{grn}>choose release-group: {wht}"))

    if num == 0:
        print(f"{red}exiting...{wht}")
        exit()

    mbid = content["release-groups"][num-1]["id"]
    title = content["release-groups"][num-1]["title"]

    for illegal in ["/","\\",":","*","?","\"","<",">"]:
        folder = title.replace(illegal,"_")

    if config.make_files_dir:
        try: os.mkdir(f"files")
        except: None

    if config.verbose:
        print(f"\n{grn}download started{wht}")

        try: os.mkdir(f"files/{folder}")
        except: print(f"{red}could not make album directory{wht}")

        print(f"starting lookup_rg with")
        print(f"  mbid: {mbid}\n  folder: {folder}")
    else:
        try: os.mkdir(get_path(["files",folder]))
        except: None

    lookup_rg(mbid,folder)


#main function
#this asks you for query to search for
#type "limit [num]" to change number of results
def main(query):
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
    parser = argparse.ArgumentParser(
    description='MusicBrainz artwork downloader')

    #positional args
    parser.add_argument("search",
    help="search for an album")

    #optional args
    parser.add_argument("-l","--limit",
    help="number of results shown",type=int)

    parser.add_argument("-v","--verbose",
    help="increase output verbosity",action="store_true")

    parser.add_argument("--version",
    help="show version and exit",action="version",version=__version__)

    parser.add_argument("-rd","--re-download",
    help="re-downloads existing files",action="store_true")

    #parsing args
    args = parser.parse_args()

    #changing config accroding to the args
    config.verbose = args.verbose
    if args.limit: config.limit == args.limit
    if args.re_download: config.skip_existing == False
    print(args.search,args.limit,args.verbose,args.re_download)

    #calling the main function
    main(args.search)
