#!/usr/bin/env python3

"""
Musicbrainz artwork downloader
start by searching for an album and select it
it'll get all the results and downloads them one by one

https://github.com/AminurAlam/musicbrainzpy

https://musicbrainz.org/doc/MusicBrainz_API
https://musicbrainz.org/doc/MusicBrainz_API/Search
https://musicbrainz.org/doc/Cover_Art_Archive/API
"""

__version__ = "1.4.0"
__author__ = "AminurAlam"

import os
import sys
import logging
import requests
import argparse
import pybrainz
from argparse import RawDescriptionHelpFormatter


# you can change default Configs here
# or pass arguments to change them eachtime
class Config:
    out_path = "Covers"        # folder to download in
    image_filter = "front"     # all/front/back/booklet/obi/medium
    search_filter = "all"      # all/album/single/ep/other
    search_limit = 5           # number of results shown


def download_art(link: str, path: str, types: list):
    """
    takes link of artwork and downloads them in
    ./Covers/{artist}-{album}/{id}.jpg
    """
    type_and_path = f"[{', '.join(types)}] {path.split('/')[-1]}"

    if os.path.exists(path):
        print(f"     {type_and_path}  {ylw}skipping, file exists{wht}")
    elif args.dry_run:
        print(f"     {type_and_path}  {ylw}skipping, dry run{wht}")
    else:
        resp = requests.get(link)
        content = resp.content
        logging.debug(f"saving file to {path}")
        with open(path, "wb+") as imgfile:
            imgfile.write(content)

        print(f"     {type_and_path}  {grn}done{wht}")


def get_releases(releases: list, folder: str):
    """
    takes releases directly from search reasults
    then gets links of releases from caa
    """

    print(f"{folder}")
    print(f"No of releases: {len(releases)}\n")

    for index, release in enumerate(releases):
        index = str(index).zfill(2)
        release_mbid: str = release.get("id")
        meta = pybrainz.release_art(release_mbid)

        print(f"[{ylw}{index}{wht}] {release_mbid}")

        if meta.get("error") is None:
            for image in meta["images"]:
                types: list = image.get("types", [])
                link: str = image.get("image")
                id: str = image.get("id")
                name: str = f"{index}-{str(id)}.{link.split('.')[-1]}"
                path: str = os.path.join(Config.out_path, folder, name)
        
                if Config.image_filter == "all":
                    download_art(link, path, types)
                elif Config.image_filter.title() in types:
                    download_art(link, path, types)
                elif Config.image_filter.title() in types:
                    download_art(link, path, types)
                elif Config.image_filter.title() in types:
                    download_art(link, path, types)
                elif Config.image_filter.title() in types:
                    download_art(link, path, types)
                elif Config.image_filter.title() in types:
                    download_art(link, path, types)
           
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

    # TODO: support offset
    content = pybrainz.search_release_group(query, limit)
    n = 0

    # filtering using -fs / --filter-search
    if Config.search_filter == "album":
        filtered_releases = [release for release in content["release-groups"]
                             if release.get("primary-type") == "Album"]
    elif Config.search_filter == "single":
        filtered_releases = [release for release in content["release-groups"]
                             if release.get("primary-type") == "Single"]
    elif Config.search_filter == "ep":
        filtered_releases = [release for release in content["release-groups"]
                             if release.get("primary-type") == "EP"]
    elif Config.search_filter == "other":
        filtered_releases = [release for release in content["release-groups"]
                             if release.get("primary-type") == "Other"]
    else:
        filtered_releases = content["release-groups"]

    if len(filtered_releases) == 0:
        sys.exit(f"{red}no releases found{wht}")

    for n, dic in enumerate(filtered_releases, start=1):
        artist: str = ", ".join([name["name"] for name in dic["artist-credit"]])
        primary_type: str = dic.get("primary-type", "none")
        secondary_types: list = dic.get("secondary-types")
        title: str = dic.get("title")
        releases: list = dic.get("releases")

        if secondary_types:
            type_str = f"{primary_type}, {', '.join(secondary_types)}"
        else:
            type_str = primary_type

        print(f"[{ylw}{n}{wht}] [{type_str}] {len(releases)} releases")
        print(f"{blu}{artist} - {title}{wht}\n")

    num = int(input(f"{grn}>choose release-group: {wht}"))

    # clearing screen when done remove if escape code isnt supported
    # TODO: change by -d / --disable-color
    for _ in range((n*3)+1):
        sys.stdout.write('\x1b[1A')
        sys.stdout.write('\x1b[2K')
    print()

    if num == 0:
        sys.exit(f"{red}exiting...{wht}")
    else:
        # getting info of selected release-group
        release_group: dict = content["release-groups"][num-1]
        releases: list = release_group["releases"]
        folder: str = f"{release_group['artist-credit'][0]['name']} - {release_group['title']}"

    # removing any illegal character from name
    for illegal_char in ["/", "\\", ":", "*", "?", "\"", "<", ">"]:
        folder = folder.replace(illegal_char, "")

    if not os.path.exists(os.path.join(Config.out_path, folder)):
        os.mkdir(os.path.join(Config.out_path, folder))

    return releases, folder


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter,
        epilog="format query like `{artist} - {album}` to get better results")

    parser.add_argument("query",
                        help="search for an album")
    parser.add_argument("-l", "--limit",
                        help="number of results shown",
                        type=int,
                        metavar="NUM",
                        default=Config.search_limit)
    parser.add_argument("-v", "--verbose",
                        help="change logging level to debug",
                        action="store_true")
    parser.add_argument("-V", "--version",
                        help="show version and exit",
                        action="version",
                        version=f"%(prog)s {__version__}")
    parser.add_argument("-n", "--dry-run",
                        help="run without downloading",
                        action="store_true")
    parser.add_argument("-d", "--disable-color",
                        help="removes colors",
                        action="store_true")
    parser.add_argument("-o", "--outdir",
                        help="change the output directory",
                        type=str,
                        metavar="PATH",
                        default=Config.out_path)
    parser.add_argument("-fi", "--filter-image",
                        help="filter images",
                        choices=["all", "front", "back",
                                 "booklet", "obi", "medium"],
                        type=str,
                        default=Config.image_filter,
                        metavar="TYPE")
    parser.add_argument("-fs", "--filter-search",
                        help="filter search results",
                        choices=["all", "album",
                                 "single", "ep", "other"],
                        type=str,
                        default=Config.search_filter,
                        metavar="TYPE")

    args = parser.parse_args()

    # changing config
    Config.out_path = args.outdir
    Config.search_limit = args.limit
    Config.image_filter = args.filter_image
    Config.search_filter = args.filter_search

    color = not args.disable_color
    red = "\33[31m" if color else ""
    grn = "\33[32m" if color else ""
    ylw = "\33[33m" if color else ""
    blu = "\33[36m" if color else ""
    wht = "\33[00m" if color else ""

    # logging
    if args.verbose:
        logging.basicConfig(
            format="[%(levelname)s] %(message)s",
            level=logging.DEBUG,)
        req = logging.getLogger("requests")
        req.setLevel(logging.INFO)
    else:
        logging.basicConfig(
            format="[%(levelname)s] %(message)s")

    logging.debug(f"{ylw}==== ARGS ===={wht}")
    for k, v in args.__dict__.items():
        logging.debug(f"  {k}: {v}")

    releases, folder = search_rg(args.query, Config.search_limit)
    get_releases(releases, folder)
