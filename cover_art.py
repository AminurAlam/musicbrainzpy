#!/usr/bin/env python3

"""
Musicbrainz artwork downloader
start by searching for an album and select it
it'll get all the results and downloads them one by one

importaint links:
    https://github.com/AminurAlam/musicbrainzpy
    https://musicbrainz.org/doc/MusicBrainz_API
"""

__version__ = "1.6.0"
__author__ = "AminurAlam"
__url__ = "https://github.com/AminurAlam/musicbrainzpy"

import os
import argparse
import musicbrainz_api as mbz_api


def process_releases(releases: list[dict], folder_name: str) -> None:
    for n, release in enumerate(releases, start=1):
        release_mbid: str = release['id']
        release_data: dict = mbz_api.release_art(release_mbid)

        print(f"[{ylw}{n:02d}{wht}] https://musicbrainz.org/release/{release_mbid}")

        if release_data.get('error') and "No cover art found" in release_data['response'].text:
            print(f"     {ylw}[!]{wht} no images")
            continue

        for image in release_data['images']:
            link: str = image.get('image')  # TODO
            file: str = f"{n:02d}-{image['id']}.{link.split('.')[-1]}"
            path: str = os.path.join(folder_name, file)
            typestr: str = ", ".join(image.get('types'))

            if Config.image == "all" or Config.image.title() in image.get('types'):
                if os.path.exists(path):
                    print(f"     {ylw}[!]{wht} skipping, file exists [{typestr}]")
                elif Config.dry_run:
                    print(f"     {ylw}[!]{wht} skipping, dry run [{typestr}]")
                else:
                    # size: str = mbz_api.get_size(link)
                    print(f"     {ylw}[…]{wht} downloading [{typestr}]")
                    mbz_api.save(link, path)
                    print('\x1b[1A\x1b[2K', end="")
                    print(f"     {grn}[✓]{wht} [{typestr}]")


def search_rg(query: str) -> tuple[list, str]:
    rgs: list[dict] = mbz_api.search_release_group(query, Config.limit, 0)['release-groups']

    if Config.search != "all":  # filtering the search results we got using -fs / --filter-search
        rgs = list(filter(lambda rg: rg.get('primary-type', '').lower() == Config.search, rgs))

    if not rgs:  # exits if everything gets filtered out
        raise Exception("no search results, try changing filter or increasing limit")

    rgs.sort(reverse=True, key=lambda rg: rg['score']*len(rg['releases']))  # sorting so first item is top result

    for n, rg in enumerate(rgs, start=1):
        # [name['name'] for name in rg['artist-credit']])
        # [rg.get('primary-type', 'none')].extend(rg.get('secondary-types', []))
        print(f"[{ylw}{n}{wht}] {grn}{', '.join([name['name'] for name in rg['artist-credit']])}", end="")
        print(f" - {rg.get('title')}{wht} ({rg['count']} {rg.get('primary-type', 'none')})")

    choice: str = input(f"{grn}\n>choose release-group: {wht}")
    print('\x1b[1A\x1b[2K' * (len(rgs) + 2))  # clearing screen/search results
    if choice == "0": exit()
    rg: dict = rgs[0] if choice == "" else rgs[int(choice)-1]

    name: str = f"{rg['artist-credit'][0]['name']} - {rg['title']}".replace("/", '-')
    rg_folder_name = os.path.join(Config.path, name)

    if not os.path.exists(rg_folder_name) and not Config.dry_run: os.makedirs(rg_folder_name)

    print(f"{name} ({rg['count']})\nhttps://musicbrainz.org/release-group/{rg['id']}\n")

    return rg['releases'], rg_folder_name


def get_args() -> tuple:
    parser = argparse.ArgumentParser()
    parser.add_argument("query",
        help="name of the album")
    parser.add_argument("-l", "--limit",
        help="max number of results displayed",
        type=int,
        metavar="NUM")
    parser.add_argument("-n", "--dry-run",
        help="run without downloading artwork",
        action="store_true")
    parser.add_argument("-o", "--outdir",
        help="change the output directory",
        type=str,
        metavar="PATH")
    parser.add_argument("-fi", "--filter-image",
        help="filter images",
        type=str,
        metavar="TYPE",
        choices=["all", "front", "booklet", "medium"])
    parser.add_argument("-fs", "--filter-search",
        help="filter search results",
        type=str,
        metavar="TYPE",
        choices=["all", "album", "single", "ep", "broadcast", "other"])

    args = parser.parse_args()

    class Config:
        limit = args.limit or 5               # number of results shown
        dry_run = args.dry_run or False       # run without downlading
        path = args.outdir or "Covers"        # folder to download in
        image = args.filter_image or "front"  # all/front/back/booklet/obi/medium
        search = args.filter_search or "all"  # https://musicbrainz.org/doc/Release_Group/Type

    return Config, args.query


if __name__ == "__main__":
    Config, query = get_args()
    grn, ylw, wht = ["\033[32m", "\033[33m", "\033[00m"] if os.name == "posix" else [""] * 3

    try: process_releases(*search_rg(query))
    except KeyboardInterrupt: exit()
