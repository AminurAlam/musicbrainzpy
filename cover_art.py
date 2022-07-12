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

__version__ = "1.4.3"
__author__ = "AminurAlam"
__url__ = "https://github.com/AminurAlam/musicbrainzpy"

import os
import sys
import logging
import argparse
import musicbrainz_api as mbz_api


class Config:
    """
    you can change default Configs here
    or pass arguments to change them every time
    using wrong option will raise error
    """

    out_path = "Covers"        # folder to download in
    image_filter = "front"     # all/front/back/booklet/obi/medium
    search_filter = "all"      # https://musicbrainz.org/doc/Release_Group/Type
    search_limit = 5           # number of results shown
    auto_select = False


def clear_lines(lines: int):
    """
    clears lines from terminal
    pass '-1' to clear whole screen

    :param lines: number of lines to be cleared
    """
    if lines == -1:
        os.system("clear")  # change to 'cls' for windows users
    else:
        for _ in range(lines):
            sys.stdout.write('\x1b[1A')
            sys.stdout.write('\x1b[2K')


def get_artwork(link: str, path: str, types: list):
    """
    take link of artwork and download them
    path of the downloaded file will look like
    ./Covers/{artist}-{album}/{id}.jpg

    :param link: link to the cover art
    :param path: path where cover art is saved
    :param types: type of art that is saved
    """

    type_str = str(types).replace("'", "")
    head = f"{' '*5}{type_str} {path.split('/')[-1]}  "

    if os.path.exists(path):
        print(f"{head}{ylw}skipping, file exists{wht}")
    elif args.dry_run:
        print(f"{head}{ylw}skipping, dry run{wht}")
    else:
        logging.debug("saving file to %s", path)
        # size: str = mbz_api.get_size(link)
        print(f"{head}{ylw}downloading…{wht}")
        mbz_api.save(link, path)
        if not args.verbose:
            clear_lines(1)
        print(f"{head}{grn}done{wht}")


def process_releases(releases: list, folder: str):
    """
    take releases from search reasults
    then gets links of releases from caa
    don't print traceback on KeyboardInterrupt

    :param releases: list containing mbid of releases
    :param folder: path of folder where files are download
    """
    for index, release in enumerate(releases, start=1):
        index = str(index).zfill(2)  # 7 -> 07
        release_mbid: str = release.get('id')
        meta: dict = mbz_api.release_art(release_mbid)

        print(f"[{ylw}{index}{wht}] {release_mbid}")

        if meta.get('error') is None:
            for image in meta['images']:
                types: list = image.get('types', [])
                link: str = image.get('image')
                id: str = image.get('id')
                name: str = f"{index}-{str(id)}.{link.split('.')[-1]}"
                path: str = os.path.join(Config.out_path, folder, name)

                if Config.image_filter == "all":
                    get_artwork(link, path, types)
                elif Config.image_filter.title() in types:
                    get_artwork(link, path, types)
        elif "No cover art found for release" in meta['response'].text:
            print(f"     {red}no images{wht}")
        else:
            print(f"     {red}unknown error{wht}")
            logging.debug("URL: %s", meta['response'].url)
            logging.debug("Exception: %s", meta['error'])
            logging.debug("%s CAA CONTENT %s", '—'*16, '—'*16)
            logging.debug("%s\n", meta['response'].text)


def auto_pick(rgs: list) -> dict:
    """
    sorts the list by comparing the scores
    caclulated by the number of releases and score from api
    returns the release-group with highest score

    :param rgs: short for release_groups
    """
    sorted_rgs = sorted(rgs,
                    reverse=True,
                    key=lambda r:
                        r['score']*len(r['releases']))

    if args.verbose:
        for rg in sorted_rgs:
            artist: str = rg['artist-credit'][0]['name']
            album: str = rg['title']
            p_type: str = rg.get('primary-type', 'None')

            print(f"  [{rg['score']*len(rg['releases'])}]",
                  f"[{p_type}] {artist} - {album}")

    return sorted_rgs[0]


def manual_pick(rgs: list) -> dict:
    """
    prints all the results for user to select
    clears the results after selection
    returns the selected release-group

    :param rgs: short for release_groups
    """
    n = 0
    for n, dic in enumerate(rgs, start=1):
        artists: list = [name['name'] for name in dic['artist-credit']]
        artist: str = " ,".join(artists)
        p_type: str = dic.get('primary-type', 'None')
        s_type: list = dic.get('secondary-types')
        releases: list = dic.get('releases')
        type_str: str = f"{p_type}, {', '.join(s_type)}" if s_type else p_type

        print(f"[{ylw}{n}{wht}] [{type_str}] ({len(releases)} releases)")
        print(f"{blu}{artist} - {dic.get('title')}{wht}\n")

    index = int(input(f"{grn}>choose release-group: {wht}"))

    # clearing screen when done, remove if escape code isnt supported
    clear_lines((n*3)+1)

    if index == 0:
        sys.exit(f"{red}exiting...{wht}")
    else:
        index -= 1
        return rgs[index]


def search_rg(query: str, limit: int):
    """
    print the search results for a query
    from which choose the release to download

    :param query:
    :param limit:
    """

    # making a directory to use
    if not os.path.exists(Config.out_path) and not args.dry_run:
        os.mkdir(Config.out_path)

    response = mbz_api.search_release_group(query, limit, 0)
    release_groups = response['release-groups']

    # filtering using -fs / --filter-search
    def checker(rgs) -> bool:
        return rgs.get('primary-type') and \
            rgs.get('primary-type').lower() == Config.search_filter

    if Config.search_filter == "all":
        rgs: list = release_groups
    else:
        rgs: list = list(filter(checker, release_groups))

    if len(rgs) == 0:
        sys.exit(f"{red}no releases found{wht}")

    # after getting release_groups aka rgs pick the release_group
    # either automatically or manually
    if Config.auto_select:
        release_group: dict = auto_pick(rgs)
    else:
        release_group: dict = manual_pick(rgs)
    artist: str = release_group['artist-credit'][0]['name']
    album: str = release_group['title']
    name: str = f"{artist} - {album}"
    releases: list = release_group['releases']

    # removing any illegal character from name
    for illegal_char in ['/', '\\', ':', '*', '?', '"', '<', '>']:
        name = name.replace(illegal_char, '')

    name_path = os.path.join(Config.out_path, name)
    if not os.path.exists(name_path) and not args.dry_run:
        os.mkdir(name_path)

    print(name, f"releases: {len(releases)}",
          f"mbid: {release_group['id']}", "—"*42, sep='\n')

    return releases, name


def get_args():
    """
    uses argparse to get user input
    """
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

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
                f"requests v{mbz_api.requests.__version__}\n" +
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
        choices=["all", "album", "single",
                 "ep", "broadcast", "other"],
        type=str,
        default=Config.search_filter,
        metavar="TYPE")

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

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
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")

    for k, v in args.__dict__.items():
        logging.debug("  %s: %s", k, v)

    releases, folder = search_rg(args.query, Config.search_limit)
    try:
        process_releases(releases, folder)
    except KeyboardInterrupt:
        sys.exit(f"{red}keyboard interrupt{wht}")
