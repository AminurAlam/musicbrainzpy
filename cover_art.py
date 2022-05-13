#!/usr/bin/env python3

"""
Musicbrainz artwork downloader
start by searching for an album and select it
it'll get all the results and downloads them one by one

https://github.com/AminurAlam/musicbrainzpy

https://musicbrainz.org/doc/MusicBrainz_API
https://musicbrainz.org/doc/Cover_Art_Archive/API
"""

__version__ = "1.3.7"
__author__ = "AminurAlam"


import os
import sys
import logging
import requests
import argparse
import pybrainz
import multiprocessing


# you can change default Configs here
# or pass arguments to change them eachtime
class Config:
    fdr_name = "Covers"     # folder to download in
    dl_type = "front"       # all/front/back/booklet//medium/obi


def download_art(link, path, types):

    main_str = f"[{', '.join(types)}] {path.split('/')[-1]}"

    if os.path.exists(path):
        print(f"     {main_str}  {ylw}file exists, skipping{wht}")

    else:
        resp = requests.get(link)
        content = resp.content

        with open(path, "wb+") as imgfile
            imgfile.write(content)
        print(f"     {main_str}  {grn}done{wht}")


def process_art(meta, folder: str, country="NA"):
    """
    downloads artwork to the folder
    ./Covers/{folder}/{id}.jpg
    """

    for image in meta["images"]:
        types = image.get("types", [])
        link = image.get("image")
        id = image.get("id", link.split("/")[-1].split(".")[0])
        name = f"{str(id)}-{country}.{link.split('.')[-1]}"
        path = os.path.join(Config.fdr_name, folder, name)

        def add(link, path, types):
            prc = multiprocessing.Process(
                target=download_art,
                args=(link, path, types))
            prc.start()
            return prc

        if Config.dl_type == "all":
            process = add(link, path, types)

        elif Config.dl_type == "front":
            if image.get("front") or ("Front" in types):
                process = add(link, path, types)

        elif Config.dl_type == "back":
            if image.get("back") or ("Back" in types):
                process = add(link, path, types)

        elif Config.dl_type == "booklet":
            if "Booklet" in types:
                process = add(link, path, types)

        else:
            print(f"{red}invalid dl_type in Config{wht}")

    process.join()


def lookup_rg(mbid, folder):
    """
    takes mbid of release-group and gets mbid of all releases
    then gets links of releases from caa
    """

    content = pybrainz.lookup_release_group(mbid)
    print(f"{folder}")
    print(f"No of releases: {len(content['releases'])}\n")

    for dic in content['releases']:
        mbid = dic.get("id")
        date = dic.get("date", "0000")
        country = dic.get("country", "NA")
        content = pybrainz.release_group_art(mbid)

        print(f"[{ylw}{country}{wht}] {mbid} [{date}]")
        meta = pybrainz.release_art(mbid)

        if meta.get("error", None) is None:
            process_art(meta, folder, country)
        else:
            print(f"     {red}no images{wht}")
            logging.debug(f"Exception: {meta['error']}")
            logging.debug(f"{ylw}==== CAA CONTENT ===={wht}" +
                          f"\n{meta['text']}\n")


def search_rg(query: str, limit: int):
    """
    takes a query and prints results for it
    you can change the number of results shown here
    """

    # making a directory to use
    if not os.path.exists(Config.fdr_name):
        os.mkdir(Config.fdr_name)

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

    for _ in range((n*3)+1):
        sys.stdout.write('\x1b[1A')
        sys.stdout.write('\x1b[2K')
    print()

    if num == 0:
        sys.exit(f"{red}exiting...{wht}")
    else:
        main = content["release-groups"][num-1]
        mbid = main["id"]
        folder = f"{main['artist-credit'][0]['name']} - {main['title']}"

    # removing any illegal character from name
    for illegal_char in ["/", "\\", ":", "*", "?", "\"", "<", ">"]:
        folder = folder.replace(illegal_char, "_")

    if not os.path.exists(os.path.join(Config.fdr_name, folder)):
        os.mkdir(os.path.join(Config.fdr_name, folder))

    lookup_rg(mbid, folder)


if __name__ == "__main__":

    red = "\33[31m"
    grn = "\33[32m"
    ylw = "\33[33m"
    blu = "\33[36m"
    wht = "\33[00m"

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
    parser.add_argument("-f", "--filter",
                        help="filter images (all, front, back, booklet)",
                        type=str)
    parser.add_argument("-g", "--group",
                        help="group images by (size, type, region, release)",
                        type=str)
    parser.add_argument("-v", "--verbose",
                        help="change logging level to debug",
                        action="store_true")
    parser.add_argument("-V", "--version",
                        help="show version and exit",
                        action="version",
                        version=__version__)

    args = parser.parse_args()

    limit = args.limit if args.limit else 5
    if args.filter is not None:
        Config.dl_type = args.filter

    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(levelname)s] %(message)s")
    else:
        logging.basicConfig(
            format="[%(levelname)s] %(message)s")

    logging.debug(f"{ylw}==== ARGS ===={wht}")
    for k, v in args.__dict__.items():
        logging.debug(f"  {k}: {v}")

    logging.debug(f"{ylw}==== CONFIG ===={wht}")
    for k, v in Config.__dict__.items():
        logging.debug(f"  {k}: {v}")

    search_rg(args.query, limit)
