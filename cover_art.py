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

__version__ = "1.4.2"
__author__ = "AminurAlam"
__url__ = "https://github.com/AminurAlam/musicbrainzpy"

import os
import sys
import logging
import argparse
import requests  # TODO: replace with urllib3
import musicbrainz_api as mbz_api
from argparse import RawDescriptionHelpFormatter

class Config:
    """
    you can change default Configs here
    or pass arguments to change them every time
    using wrong option will raise error
    """

    out_path = "Covers"        # folder to download in
    image_filter = "front"     # all/front/back/booklet/obi/medium
    search_filter = "all"      # all/album/single/ep/other
    search_limit = 5           # number of results shown
    auto_select = False


def download_art(link: str, path: str, types: list):
    """
    take link of artwork and download them
    path of the downloaded file will look like
    ./Covers/{artist}-{album}/{id}.jpg

    :param link: link to the cover art
    :param path: path where cover art is saved
    :param types: type of art that is saved
    """

    type_str = str(types).replace("'", "")
    type_and_path = f"{type_str} {path.split('/')[-1]}"
    pad = ' '*5      # padding

    if os.path.exists(path):
        print(f"{pad}{type_and_path}  {ylw}skipping, file exists{wht}")
    elif args.dry_run:
        print(f"{pad}{type_and_path}  {ylw}skipping, dry run{wht}")
    else:
        resp = requests.get(link)
        content = resp.content
        logging.debug("saving file to %s", path)
        with open(path, "wb+") as imgfile:
            imgfile.write(content)

        print(f"{pad}{type_and_path}  {grn}done{wht}")


def process_releases(releases: list, folder: str):
    """
    take releases from search reasults
    then gets links of releases from caa
    don't print traceback on KeyboardInterrupt

    :param releases: list containing mbid of releases
    :param folder: path of folder where files are download
    """
    for index, release in enumerate(releases, start=1):
        index = str(index).zfill(2)
        release_mbid: str = release.get("id")
        meta = mbz_api.release_art(release_mbid)

        print(f"[{ylw}{index}{wht}] {release_mbid}")

        if meta.get("error") is None:
            for image in meta['images']:
                types: list = image.get("types", [])
                link: str = image.get("image")
                id: str = image.get("id")
                name: str = f"{index}-{str(id)}.{link.split('.')[-1]}"
                path: str = os.path.join(Config.out_path, folder, name)

                if Config.image_filter == "all":
                    download_art(link, path, types)
                elif Config.image_filter.title() in types:
                    download_art(link, path, types)
        else:
            print(f"     {red}no images{wht}")
            logging.debug("Exception: %s", meta['error'])
            logging.debug("%s ===== CAA CONTENT ===== %s", ylw, wht)
            logging.debug("%s\n", meta['text'])


def auto_pick(rgs: list):
    """
    calc
    """
    sorted_rgs = []
    for dic in rgs:
        sorted_rgs = sorted(rgs,
                    key=lambda dic:
                        dic['score']*len(dic.get('releases')),
                    reverse=True)

    for n, dic in enumerate(sorted_rgs, start=1):
        artist: str = dic['artist-credit'][0]['name']
        p_type: str = dic.get("primary-type", "None")

        logging.debug(f"[{n} - {p_type}] {artist} - {dic.get('title')}")

    return sorted_rgs[0]


def manual_pick(rgs: list):
    """
    manual
    """
    n = 0
    for n, dic in enumerate(rgs, start=1):
        artist: str = ", ".join([name['name'] for name in dic['artist-credit']])
        p_type: str = dic.get("primary-type", "None")
        s_type: list = dic.get("secondary-types")
        releases: list = dic.get("releases")
        type_str = f"{p_type}, {', '.join(s_type)}" if s_type else p_type

        print(f"[{ylw}{n}{wht}] [{type_str}] {ylw}{len(releases)*dic.get('score')}{wht}")
        print(f"{blu}{artist} - {dic.get('title')}{wht}\n")

    index = int(input(f"{grn}>choose release-group: {wht}"))

    # clearing screen when done, remove if escape code isnt supported
    for _ in range((n*3)+1):
        sys.stdout.write('\x1b[1A')
        sys.stdout.write('\x1b[2K')
    print()

    if index == 0:
        sys.exit(f"{red}exiting...{wht}")
    else:
        index -= 1
        releases: list = rgs[index]['releases']
        name: str = f"{rgs[index]['artist-credit'][0]['name']} - {rgs[index]['title']}"

    return rgs[index]


def search_rg(query: str, limit: int):
    """
    print the search results for a query
    from which choose the release to download

    :param query:
    :param limit:
    :return:
    """

    # making a directory to use
    if not os.path.exists(Config.out_path):
        os.mkdir(Config.out_path)

    release_groups = mbz_api.search_release_group(query, limit)['release-groups']

    # filtering using -fs / --filter-search
    if Config.search_filter == "album":
        rgs = [release for release in release_groups
                             if release.get("primary-type") == "Album"]
    elif Config.search_filter == "single":
        rgs = [release for release in release_groups
                             if release.get("primary-type") == "Single"]
    elif Config.search_filter == "ep":
        rgs = [release for release in release_groups
                             if release.get("primary-type") == "EP"]
    elif Config.search_filter == "other":
        rgs = [release for release in release_groups
                             if release.get("primary-type") == "Other"]
    else:
        rgs = release_groups

    if len(rgs) == 0:
        sys.exit(f"{red}no releases found{wht}")

    # after getting release_groups pick the release_group
    # either automatically or manually
    if Config.auto_select:
        release_group: dict = auto_pick(rgs)
    else:
        release_group: dict = manual_pick(rgs)

    name: str = f"{release_group['artist-credit'][0]['name']} - {release_group['title']}"
    releases: list = release_group['releases']

    # removing any illegal character from name
    for illegal_char in ['/', '\\', ':', '*', '?', '"', '<', '>']:
        name = name.replace(illegal_char, '')

    if not os.path.exists(os.path.join(Config.out_path, name)):
        os.mkdir(os.path.join(Config.out_path, name))

    print(name)
    print(f"releases: {len(releases)}")
    print(f"mbid: {release_group['id']}")
    print("—"*len(release_group['id']) + "—"*6)

    return releases, name


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter,
        # TODO: implement this
        epilog="format query like `{artist} - {album}` to get better results")

    parser.add_argument("query",
        help="name of the album")
    parser.add_argument("-l", "--limit",
        help="max number of results displayed",
        type=int,
        metavar="NUM",
        default=Config.search_limit)
    parser.add_argument("-a", "--auto-select",
        help="automatically pick the best search result",
        action="store_true")
    parser.add_argument("-v", "--verbose",
        help="change logging level to debug",
        action="store_true")
    parser.add_argument("-V", "--version",
        help="show version and exit",
        action="version",
        version=f"MusicBrainzPy v{__version__}\n" +
                f"MusicBrainz_API v{mbz_api.__version__}\n" +
                f"Python v{sys.version.split()[0]}\n\n" +
                f"running on `{sys.platform}` {os.name}\n" +
                f"filename:  {os.curdir}/%(prog)s") 
    parser.add_argument("-n", "--dry-run",
        help="run without downloading artwork",
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
    Config.auto_select = args.auto_select

    color = not args.disable_color
    red = "\33[31m" if color else ""
    grn = "\33[32m" if color else ""
    ylw = "\33[33m" if color else ""
    blu = "\33[36m" if color else ""
    wht = "\33[00m" if color else ""

    # logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG,
            format="%(message)s")

    logging.debug("—"*18 + " %sARGS%s " + "—"*18, ylw, wht)
    for k, v in args.__dict__.items():
        logging.debug("    %s: %s", k, v)

    releases, folder = search_rg(args.query, Config.search_limit)
    try:
        process_releases(releases, folder)
    except KeyboardInterrupt:
        sys.exit(f"\n{red}keyboard interrupt{wht}")
