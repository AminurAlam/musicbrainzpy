#!/usr/bin/env python3

"""
Musicbrainz artwork downloader
start by searching for an album and select it
it'll get all the results and downloads them one by one

https://github.com/AminurAlam/musicbrainzpy

https://musicbrainz.org/doc/MusicBrainz_API
https://musicbrainz.org/doc/Cover_Art_Archive/API
"""

__version__ = "1.3.5"
__author__ = "AminurAlam"


import os
import sys
import wget
import json
import logging
import requests
import argparse
import pybrainz


# colors
red = "\33[31m"
grn = "\33[32m"
ylw = "\33[33m"
blu = "\33[36m"
wht = "\33[00m"


# you can change default Configs here
# or pass arguments to change them everytime
class Config:
    make_fdir = True        # makes folder with name fdr_name if not present
    skip_existing = True    # skips in file is already present

    dl_type = "front"       # all, front, back, booklet
    fdr_name = "Covers"     # dont use illegal characters
    dl_tool = "wget"        # default, wget, curl


def artdl(meta, folder, country="NA"):
    """
    takes links, folder and country
    and downloads artwork to the folder
    files/{folder}/{id}.jpg
    """
    for image in meta["images"]:
        front = image.get("front", False)
        back = image.get("back", False)
        types = image.get("types", [])
        link = image.get("image", "https://example.org")
        id = image.get("id", link.split("/")[-1].split(".")[0])
        name = f"{str(id)}-{country}.{link.split('.')[-1]}"
        path2 = os.path.join(Config.fdr_name, folder, name)

        def save(link, path):
            print(f"[{', '.join(types)}] {path.split('/')[-1]}")

            try:
                open(path)
                if Config.skip_existing:
                    print(f"{ylw}file exists, skipping{wht}\n")
                else:
                    raise Exception

            except Exception:
                if Config.dl_tool == "default":
                    resp = requests.get(link)
                    content = resp.content
                    with open(path, "wb+") as imgfile:
                        imgfile.write(content)
                elif Config.dl_tool == "wget":
                    wget.download(link, path)
                    sys.stdout.write("\x1b[2K\n")
                else:
                    print(f"{red}invalid 'dl_tool' in Config'")
                    print(f"fix your Config and try again{wht}")

        if Config.dl_type == "all":
            save(link, path2)

        elif Config.dl_type == "front":
            if front or "Front" in types:
                save(link, path2)

        elif Config.dl_type == "back":
            if back or "Back" in types:
                save(link, path2)

        else:
            print(f"{red}invalid dl_type in Config{wht}")


def lookup_rg(mbid, folder):
    """
    takes mbid of release-group and gets mbid of all releases
    then gets links of releases from caa
    """

    content = pybrainz.lookup_release_group(mbid)

    for dic in content["releases"]:
        mbid = dic.get("id")
        date = dic.get("date", "0000")
        country = dic.get("country", "NA")
        content = pybrainz.release_group_art(mbid)

        print(f"[{ylw}{country}{wht}] {mbid} [{date}]")
        meta = pybrainz.release_art(mbid)

        if meta.get("error", None) is None:
            artdl(meta, folder, country)
        else:
            logging.warning(f"{red}no images{wht}")
            logging.debug("{ylw} === CAA RESPONSE === {wht}")
            logging.debug(json.dumps(meta, indent=2))

    print("Downloading finished.")


def search_rg(query: str, limit: int):
    """
    takes a query and prints results for it
    you can change the number of results shown here
    """

    # making a directory to use
    if not os.path.exists(Config.fdr_name):
        os.mkdir(Config.fdr_name)

    # content = request(f"?query={query}&limit={limit}&fmt=json")
    content = pybrainz.search_release_group(query, limit)

    n = 0
    for n, dic in enumerate(content["release-groups"], start=1):
        artist = ", ".join([name["name"] for name in dic["artist-credit"]])
        ptype = dic.get("primary-type", "not found")
        title = dic.get("title", "not found")
        id = dic.get("id", "not found")

        print(f"[{ylw}{n}{wht}] [{ptype}] {id}")
        print(f"{blu}{artist} - {title}{wht}\n")

    num = int(input(f"{grn}>choose release-group: {wht}"))

    for i in range(n*3+1):
        sys.stdout.write('\x1b[1A')
        sys.stdout.write('\x1b[2K')

    if num == 0:
        sys.exit(f"{red}exiting...{wht}")

    mbid = content["release-groups"][num-1]["id"]
    title = content["release-groups"][num-1]["title"]
    folder = title

    # removing any illegal character from name
    for illegal_char in ["/", "\\", ":", "*", "?", "\"", "<", ">"]:
        folder = folder.replace(illegal_char, "_")

    logging.info(f"\n{grn}download started{wht}")
    logging.info("starting lookup_rg with:")
    logging.info(f"  mbid: {mbid}\n  folder: {folder}")

    if not os.path.exists(os.path.join(Config.fdr_name, folder)):
        os.mkdir(os.path.join(Config.fdr_name, folder))

    lookup_rg(mbid, folder)


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
    parser.add_argument("-l", "--limit",
                        help="number of results shown",
                        type=int)
    parser.add_argument("-v",
                        "--verbose",
                        help="change logging level to debug",
                        action="store_true")
    parser.add_argument("-V",
                        "--version",
                        help="show version and exit",
                        action="version",
                        version=__version__)
    parser.add_argument("-rd",
                        "--re-download",
                        help="re-downloads existing files",
                        action="store_true")

    args = parser.parse_args()

    # changing Config accroding to the args
    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(levelname)s] %(message)s")

    if args.re_download:
        Config.skip_existing = False

    logging.debug(f"{ylw} === CONFIG === {wht}")
    for k, v in Config.__dict__.items():
        logging.debug(f" {k} : {v}")

    logging.debug(f"{ylw} === ARGS === {wht}")
    logging.debug(json.dumps(
        args.__dict__,
        indent=2))

    limit = args.limit if args.limit else 5
    Config.skip_existing = args.re_download

    search_rg(args.query, limit)
