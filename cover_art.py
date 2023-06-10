#!/usr/bin/env python3
"""
Musicbrainz artwork downloader
start by searching for an album and select it
it'll get all the results and downloads them one by one

important links:
    https://github.com/AminurAlam/musicbrainzpy
    https://musicbrainz.org/doc/MusicBrainz_API
"""

__version__ = "1.6.5"

import os
import api
import argparse


def download_releases(rg: dict) -> None:
    rg_path = os.path.join(args.outdir, rg['title'].replace("/", '-'))
    os.path.exists(rg_path) or os.makedirs(rg_path)

    for n, release in enumerate(rg['releases'], start=1):
        mbid: str = release['id']
        print(f"[{ylw}{n:02d}{wht}] https://musicbrainz.org/release/{mbid}")

        for image in api.ia_req(release['id']).get('images', []):
            if args.image != "all" and args.image.title() not in image.get('types'): continue

            filename: str = image.get('image').split("/")[-1]
            link: str = f"https://archive.org/download/mbid-{mbid}/mbid-{mbid}-{filename}"
            img_path = os.path.join(rg_path, f"{n:02d}-{filename}")

            if os.path.exists(img_path):
                print(f"     {ylw}[!]{wht} file already exists")
                continue

            print(f"     {ylw}[…]{wht} downloading [{', '.join(image.get('types'))}]")
            size: int = api.save(link, img_path, args.size)
            if size:
                print(f"\x1b[1A\x1b[2K     {grn}[✓]{wht} {size//1000}kb [{', '.join(image.get('types'))}]")
            else:
                print(f"\x1b[1A\x1b[2K     {ylw}[!]{wht} file is too small {size//1000}kb")


def search_rg(query: str) -> dict:
    rgs: list[dict] = api.search("release-group", query, args.limit, 0)['release-groups']

    if args.search != "all":  # filtering the search results by --filter-search
        rgs = list(filter(lambda rg: rg.get('primary-type', '').lower() == args.search, rgs))

    if not rgs:
        raise Exception("no search results. try changing filter, increasing limit")

    rgs.sort(reverse=True, key=lambda rg: rg['score'] * len(rg['releases']))

    for n, rg in enumerate(rgs, start=1):
        artists: str = ", ".join([name['name'] for name in rg['artist-credit']])
        types: str = ", ".join([rg.get('primary-type', 'none')] + rg.get('secondary-types', []))
        print(f"[{ylw}{n}{wht}] {grn}{artists} - {rg.get('title')}{wht} ({rg['count']} {types})")

    choice: str = input("\n>choose release-group: ")
    choice == "0" and exit()
    print('\x1b[1A\x1b[2K' * (len(rgs) + 2))  # clearing screen/search results

    return rgs[0] if choice == "" else rgs[int(choice) - 1]


if __name__ == "__main__":

    class Formatter(argparse.HelpFormatter):  # fixes --help
        def __init__(self, *args, **kwargs):
            super().__init__(max_help_position=40, *args, **kwargs)

    parser = argparse.ArgumentParser(formatter_class=Formatter)
    parser.add_argument("query", help="name of the album", type=str)
    parser.add_argument("-l", "--limit",
        help="limit the number of results displayed",
        type=int, default=5, metavar="NUM")
    parser.add_argument("-o", "--outdir",
        help="change the output directory where files are saved",
        type=str, default="Covers", metavar="PATH")
    parser.add_argument("-i", "--filter-image",
        help="filter the type of images saved",
        type=str, dest="image", default="front", metavar="TYPE",
        choices=["all", "front", "back", "booklet", "medium"])
    parser.add_argument("-s", "--filter-search",
        help="filter search results",
        type=str, dest="search", default="all", metavar="TYPE",
        choices=["all", "album", "single", "ep", "broadcast", "other"])
    parser.add_argument("-b", "--filter-size",
        help="filter images by filesize (in kb)",
        type=int, dest="size", default=0, metavar="SIZE")

    args = parser.parse_args()
    if os.name == "nt": os.system("")  # enables ansi escape sequence
    grn, ylw, wht = "\033[32m", "\033[33m", "\033[00m"  # who needs colorama anyway

    download_releases(search_rg(args.query))
