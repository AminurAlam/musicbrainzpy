#!/usr/bin/env python3

"""
Musicbrainz artwork downloader
start by searching for an album and select it
it'll get all the results and downloads them one by one

https://github.com/AminurAlam/musicbrainzpy

https://musicbrainz.org/doc/MusicBrainz_API
https://musicbrainz.org/doc/Cover_Art_Archive/API
"""

import os
from os import sep
import json, requests, argparse
import wget

#info
__version__ = "1.3.1"
__author__ = "AminurAlam"

#colors
red="\33[31m"
grn="\33[32m"
ylw="\33[33m"
blu="\33[36m"
wht="\33[00m"

#you can change default configs here
#or pass arguments to change them everytime
class config:
    make_fdir = True        #makes folder with name fdr_name if not present
    skip_existing = True    #skips in file is already present
    verbose = False         #change verbosity of logging

    dl_type = "front"            #all, front, back, booklet
    fdr_name = "Covers"     #dont use illegal characters
    limit = "5"             #keep btwn 1-50
    dl_tool = "wget"        #default, wget, curl


def artdl(meta,folder,country="NA"):
    """
    takes links, folder and country
    and downloads artwork to the folder
    files/{folder}/{id}.jpg
    """
    for image in meta["images"]:

        try: front = image["front"]
        except: front = False

        try: back = image["back"]
        except: back = False

        try: types = image["types"]
        except: types = []

        try: link = image["image"]
        except: link = "https://example.org"

        try: id = image["id"]
        except: id = link.split("/")[-1].split(".")[0]

        name = f"{str(id)}-{country}.{link.split('.')[-1]}"
        path2 = sep.join([config.fdr_name,folder,name])

        def save(link,path):

            print(f"{types} {path.split(sep)[-1]}{wht}")

            try:
                open(path)

                if config.skip_existing:
                    print(f"{ylw}file exists, skipping{wht}\n")
                else: download_it_again_lol()

            except:
                if config.dl_tool == "default":
                    resp = requests.get(link)
                    content = resp.content
                    with open(path,"w+") as imgfile:
                        imgfile.write(content)

                elif config.dl_tool == "wget":
                    wget.download(link,path)

                print("\n")


        if config.dl_type == "all": save(link,path2)

        elif config.dl_type == "front":
            if front or "Front" in types: save(link,path2)

        elif config.dl_type == "back":
            if back or "Back" in types: save(link,path2)

        else: print("{red}invalid dl_type in config{wht}")


def request(head):
    """
    takes mbz links gets the results
    """
    url = "https://musicbrainz.org/ws/2/release-group" + head
    resp = requests.get(url)
    content = json.loads(resp.content.decode())

    if config.verbose:
        print(f"url: {url}\nstatus: {str(resp.status_code)}")

        with open(sep.join([config.fdr_name,"content.txt"]),"w+") as file:
            file.write(str(content))

    return content


#takes mbid of release-group and gets mbid of all releases
#then gets links of releases from caa
def lookup_rg(mbid,folder):
    """
    takes mbid of release-group and gets mbid of all releases
    then gets links of releases from caa
    """
    content = request(f"/{mbid}?fmt=json&inc=releases")

    for dic in content["releases"]:
        try: mbid = dic["id"]
        except: mbid = "not found"

        try: date = dic["date"]
        except: date = red+"0000"+wht

        try: country = dic["country"]
        except: country = "NA"

        print(f"[{ylw}{country.replace('NA','{red}NA{wht}')}{wht}] {mbid} [{date}]")

        url = f"https://coverartarchive.org/release/{mbid}"
        resp = requests.get(url)
        content = resp.content.decode()

        #tries to load links and download them
        try:
            content = json.loads(content)
            artdl(content,folder,country)

        #prints this if no images were found
        except Exception as e:
            print(f"{red}no images{wht}\n")
            if config.verbose: print(f"rg url: {url}",f"status: {resp.status_code}",f"{ylw}{content}{wht}",f"exept: {red}{e}{wht}",sep="\n")

    print("Downloading finished.")


def search_rg(query,limit="5"):
    """
    takes a query and prints results for it
    you can change the number of results shown here
    """
    if config.make_fdir:
        try: os.mkdir(config.fdr_name)
        except: None

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

        try: ptype = dic["primary-type"] #album, single, ep
        except: ptype = "not found"

        print(f"[{ylw}{n}{wht}] [{ptype}] {id}")
        print(f"{blu}{artist} - {title}{wht}\n")

    num = int(input(f"{grn}>choose release-group: {wht}"))

    if num == 0:
        print(f"{red}exiting...{wht}")
        exit()

    mbid = content["release-groups"][num-1]["id"]
    title = content["release-groups"][num-1]["title"]

    #removing any illegal character from name
    for illegal in ["/","\\",":","*","?","\"","<",">"]:
        folder = title.replace(illegal,"_")

    if config.verbose:
        print(f"\n{grn}download started{wht}")

        try: os.mkdir(sep.join([config.fdr_name,folder]))
        except: print(f"{red}could not make album directory{wht}")

        print(f"starting lookup_rg with")
        print(f"  mbid: {mbid}\n  folder: {folder}")

    else:
        try: os.mkdir(sep.join([config.fdr_name,folder]))
        except: None

    lookup_rg(mbid,folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    Musicbrainz artwork downloader
    start by searching for an album and select it
    it'll get all the results and downloads them one by one

    https://github.com/AminurAlam/musicbrainzpy

    https://musicbrainz.org/doc/MusicBrainz_API
    https://musicbrainz.org/doc/Cover_Art_Archive/API""")

    parser.add_argument("query",
    help="search for an album")

    parser.add_argument("-l","--limit",
    help="number of results shown",type=int)

    parser.add_argument("-v","--verbose",
    help="increase output verbosity",action="store_true")

    parser.add_argument("--version",
    help="show version and exit",action="version",version=__version__)

    parser.add_argument("-rd","--re-download",
    help="re-downloads existing files",action="store_true")

    args = parser.parse_args()

    #changing config accroding to the args
    config.verbose = args.verbose
    if args.limit: config.limit == args.limit
    if args.re_download: config.skip_existing == False

    if config.verbose: print(f"re-download: {args.re_download}")

    search_rg(args.query)
