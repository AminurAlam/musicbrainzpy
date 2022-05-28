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
    out_path = "Covers"        # folder to download in
    image_filter = "front"     # all/front/back/booklet/obi/medium
    search_filter = "all"      # all/album/single/ep


def download_art(link, path, types):
    type_and_path = f"[{', '.join(types)}] {path.split('/')[-1]}"

    if os.path.exists(path):
        print(f"     {type_and_path}  {ylw}file exists, skipping{wht}")
    else:
        resp = requests.get(link)
        content = resp.content
        logging.debug(f"saving file to {path}")
        with open(path, "wb+") as imgfile:
            imgfile.write(content)

        print(f"     {type_and_path}  {grn}done{wht}")


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
        path = os.path.join(Config.out_path, folder, name)

        def add(link, path, types):
            prc = multiprocessing.Process(
                target=download_art,
                args=(link, path, types))
            prc.start()
            return prc

        if Config.image_filter == "all":
            process = add(link, path, types)

        elif Config.image_filter == "front":
            if image.get("front") or ("Front" in types):
                process = add(link, path, types)

        elif Config.image_filter == "back":
            if image.get("back") or ("Back" in types):
                process = add(link, path, types)

        elif Config.image_filter == "booklet":
            if "Booklet" in types:
                process = add(link, path, types)

        elif Config.image_filter == "obi":
            if "Obi" in types:
                process = add(link, path, types)
        elif Config.image_filter == "medium":
            if "Medium" in types:
                process = add(link, path, types)

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
            logging.debug(f"{ylw} ===== CAA CONTENT ===== {wht}" +
                          f"\n{meta['text']}\n")


def search_rg(query: str, limit: int):
    """
    takes a query and prints results for it
    you can change the number of results shown here
    """

    # making a directory to use
    if not os.path.exists(Config.out_path):
        os.mkdir(Config.out_path)

    content = pybrainz.search_release_group(query, limit)
    filtered_releases = []
    n = 0
    for release in content["release-groups"]:

        if Config.search_filter == "album":
            if release.get("primary-type") == "Album":
                filtered_releases.append(release)
        elif Config.search_filter == "single":
            if release.get("primary-type") == "Single":
                filtered_releases.append(release)
        elif Config.search_filter == "ep":
            if release.get("primary-type") == "EP":
                filtered_releases.append(release)
        else:
            filtered_releases.append(release)

    for n, dic in enumerate(filtered_releases, start=1):
        artist = ", ".join([name["name"] for name in dic["artist-credit"]])
        ptype = dic.get("primary-type", "not found")
        title = dic.get("title", "not found")
        id = dic.get("id", "not found")

        print(f"[{ylw}{n}{wht}] [{ptype}] {id}")
        print(f"{blu}{artist} - {title}{wht}\n")

    len_str = f"1..{len(filtered_releases)}"
    num = int(input(f"{grn}> choose release-group [{len_str}]: {wht}"))

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

    if not os.path.exists(os.path.join(Config.out_path, folder)):
        os.mkdir(os.path.join(Config.out_path, folder))

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
                        type=int,
                        metavar="NUM")
    parser.add_argument("-f", "--filter",
                        help="filter images" +
                        "(all/front/back/booklet/obi)",
                        type=str,
                        default="front",
                        metavar="TYPE")
    parser.add_argument("-sf", "--search-filter",
                        help="filter search results" +
                             "(all/album/single/ep)",
                        type=str,
                        default="all",
                        metavar="TYPE")
    parser.add_argument("-g", "--group",
                        help="group images by" +
                             "(size/type/region/release)",
                        type=str)
    parser.add_argument("-o", "--output-dir",
                        help="change the output directory",
                        type=str,
                        metavar="PATH")
    parser.add_argument("-d", "--disable-color",
                        help="removes colors",
                        action="store_false")
    parser.add_argument("-v", "--verbose",
                        help="change logging level to debug",
                        action="store_true")
    parser.add_argument("-V", "--version",
                        help="show version and exit",
                        action="version",
                        version=__version__)

    args = parser.parse_args()

    # changing config
    limit = args.limit if args.limit else 5
    Config.out_path = args.output_dir if args.output_dir else Config.out_path

    red = "\33[31m" if args.disable_color else ""
    grn = "\33[32m" if args.disable_color else ""
    ylw = "\33[33m" if args.disable_color else ""
    blu = "\33[36m" if args.disable_color else ""
    wht = "\33[00m" if args.disable_color else ""

    if args.filter not in ["all", "front", "back", "booklet", "obi"]:
        sys.exit(f"{red}invalid image_filter selected\n" +
                 f"use: all/front/back/booklet/obi{wht}")
    else:
        Config.image_filter = args.filter

    if args.search_filter not in ["all", "album", "single", "ep"]:
        sys.exit(f"{red}invalid search_filter selected\n" +
                 f"use: all/album/single/ep{wht}")
    else:
        Config.search_filter = args.search_filter

    # logging
    if args.verbose:
        logging.basicConfig(
            format="[%(levelname)s] %(message)s",
            level=logging.DEBUG,)
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
