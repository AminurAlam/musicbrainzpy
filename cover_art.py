#!/usr/bin/env python3
"""
Musicbrainz artwork downloader
start by searching for an album and select it
it'll get all the results and downloads them one by one

important links:
    https://github.com/AminurAlam/musicbrainzpy
    https://musicbrainz.org/doc/MusicBrainz_API
"""

__version__ = "1.7.0"

import argparse
import os

import api


def download_releases(rg: dict) -> None:
    title: str = rg['title']
    for illegal_char in r':?"[|]\<*>/': title = title.replace(illegal_char, '')  # noqa: E701

    rg_path = os.path.join(args.outdir, title)
    os.path.exists(rg_path) or os.makedirs(rg_path) #pyright: ignore[reportUnusedExpression]

    for n, release in enumerate(rg['releases'], start=1):
        if args.range and not (args.range[0] <= n <= args.range[1]):
            continue

        mbid: str = release['id']
        print(f"[{ylw}{n:02d}{wht}] https://musicbrainz.org/release/{mbid}")

        for image in api.ia_req(release['id']).get('images', []):
            if args.image != "all" and args.image.title() not in image.get('types'): continue  # noqa: E701
            if "Raw/Unedited" in image.get('types'):
                print(f"     {ylw}[!]{wht} not a good scan")
                continue

            filename: str = image.get('image').split("/")[-1]
            link: str = f"https://archive.org/download/mbid-{mbid}/mbid-{mbid}-{filename}"
            img_path: str = os.path.join(rg_path, f"{n:02d}-{filename}")

            if os.path.exists(img_path):
                print(f"     {ylw}[!]{wht} file already exists")
                continue

            print(f"     {ylw}[…]{wht} downloading [{', '.join(image.get('types'))}]")
            success, size, ft = api.save(link, img_path, args)
            icon = grn + "[✓]" if success else ylw + "[!]"
            print(f"\x1b[1A\x1b[2K     {icon}{wht} {size} {ft} [{', '.join(image.get('types'))}]")


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
    choice == "0" and exit() # pyright: ignore[reportUnusedExpression]
    print('\x1b[1A\x1b[2K' * (len(rgs) + 2))  # clearing screen/search results

    return rgs[0] if choice == "" else rgs[int(choice) - 1]


if __name__ == "__main__":

    class Formatter(argparse.HelpFormatter):  # fixes --help
        def __init__(self, *args, **kwargs):
            super().__init__(max_help_position=40, *args, **kwargs)

    parser = argparse.ArgumentParser(formatter_class=Formatter)
    parser.add_argument("query", help="name of the album", type=str)
    parser.add_argument("-l",
        help="[l]imit the number of results displayed",
        type=int, dest="limit", default=5, metavar="NUM")
    parser.add_argument("-o",
        help="change the [o]utput directory where files are saved",
        type=str, dest="outdir", default="Covers", metavar="PATH")
    parser.add_argument("-i",
        help="filter the type of [i]mages saved",
        type=str, dest="image", default="front", metavar="TYPE",
        choices=["all", "front", "back", "booklet", "poster", "medium"])
    parser.add_argument("-s",
        help="filter [s]earch results",
        type=str, dest="search", default="all", metavar="TYPE",
        choices=["all", "album", "single", "ep", "broadcast", "other"])
    parser.add_argument("-b",
        help="minimum filesize allowed (in kb)",
        nargs=2, type=int, dest="size", default=[200,30_000], metavar=("min", "max"))
    parser.add_argument("-r",
        help="[r]ange of releases to download",
        nargs=2, type=int, dest="range", metavar=("start", "stop"))
    parser.add_argument("-p",
        help="download [p]df artwork if available",
        action="store_true", dest="pdf")
    parser.add_argument("-n",
        help="dont download anything",
        action="store_true", dest="dry")


    args = parser.parse_args()
    if os.name == "nt": os.system("")  # enables ansi escape sequence  # noqa: E701
    grn, ylw, wht = "\033[32m", "\033[33m", "\033[00m"  # who needs colorama anyway

    download_releases(search_rg(args.query))
