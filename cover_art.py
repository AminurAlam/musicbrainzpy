#!/usr/bin/env python3

"""
Musicbrainz artwork downloader
start by searching for an album and select it
it'll get all the results and downloads them one by one

importaint links:
    https://github.com/AminurAlam/musicbrainzpy
    https://musicbrainz.org/doc/MusicBrainz_API
"""

__version__ = "1.6.2"

import os
import argparse
import musicbrainz_api as mbz_api


def download_releases(releases: list[dict], rg_name: str) -> None:
    rg_path = os.path.join(args.outdir, rg_name)
    if not os.path.exists(rg_path): os.makedirs(rg_path)

    for n, release in enumerate(releases, start=1):
        release_mbid: str = release['id']
        release: dict = mbz_api.release_art(release_mbid)
        print(f"[{ylw}{n:02d}{wht}] https://musicbrainz.org/release/{release_mbid}")

        for image in release.get('images', []):
            link: str = image.get('image')
            img_path: str = os.path.join(rg_path, f"{n:02d}-{image['id']}.{link.split('.')[-1]}")

            if args.image != "all" and args.image.title() not in image.get('types'):
                continue

            if os.path.exists(img_path):
                print(f"     {ylw}[!]{wht} file already exists")
                continue

            print(f"     {ylw}[…]{wht} downloading [{', '.join(image.get('types'))}]")
            mbz_api.save(link, img_path)
            print('\x1b[1A\x1b[2K', end="")
            print(f"     {grn}[✓]{wht} [{', '.join(image.get('types'))}]")


def search_rg(query: str) -> tuple[list, str]:
    rgs: list[dict] = mbz_api.search_release_group(query, args.limit, 0)['release-groups']

    if args.search != "all":  # filtering the search results
        rgs = list(filter(lambda rg: rg.get('primary-type', '').lower() == args.search, rgs))

    if not rgs: raise Exception("no search results, try changing filter or increasing limit")

    rgs.sort(reverse=True, key=lambda rg: rg['score'] * len(rg['releases']))

    for n, rg in enumerate(rgs, start=1):
        artists: str = ", ".join([name['name'] for name in rg['artist-credit']])
        types: str = ", ".join([rg.get('primary-type', 'none')] + rg.get('secondary-types', []))
        print(f"[{ylw}{n}{wht}] {grn}{artists} - {rg.get('title')}{wht} ({rg['count']} {types})")

    choice: str = input("\n>choose release-group: ")
    print('\x1b[1A\x1b[2K' * (len(rgs) + 2))  # clearing screen/search results

    if choice == "0": exit()
    rg: dict = rgs[0] if choice == "" else rgs[int(choice) - 1]
    rg_name: str = f"{rg['artist-credit'][0]['name']} - {rg['title']}".replace("/", '-')
    print(f"{rg_name} ({rg['count']})\nhttps://musicbrainz.org/release-group/{rg['id']}\n")

    return rg['releases'], rg_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query",
        help="name of the album",
        type=str)
    parser.add_argument("-l", "--limit",
        help="max number of results displayed",
        type=int,
        default=5,
        metavar="NUM")
    parser.add_argument("-o", "--outdir",
        help="change the output directory",
        type=str,
        default="Covers",
        metavar="PATH")
    parser.add_argument("-i", "--filter-image",
        help="filter images",
        type=str,
        dest="image",
        default="front",
        metavar="TYPE",
        choices=["all", "front", "booklet", "medium"])
    parser.add_argument("-s", "--filter-search",
        help="filter search results",
        type=str,
        dest="search",
        default="all",
        metavar="TYPE",
        choices=["all", "album", "single", "ep", "broadcast", "other"])

    args = parser.parse_args()
    grn, ylw, wht = ["\033[32m", "\033[33m", "\033[00m"] if os.name == "posix" else [""] * 3

    download_releases(*search_rg(args.query))
