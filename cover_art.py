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

__version__ = "1.4.4"
__author__ = "AminurAlam"
__url__ = "https://github.com/AminurAlam/musicbrainzpy"

import os
import sys
import argparse
import musicbrainz_api as mbz_api


class Config:
    """
    this is a dataclass for settings
    you can change default options here
    or pass arguments to change them every time
    """

    out_path = "Covers"     # folder to download in
    image_filter = "front"  # all/front/back/booklet/obi/medium
    search_filter = "all"   # https://musicbrainz.org/doc/Release_Group/Type
    search_limit = 5        # number of results shown
    auto_select = False
    quality = 0


def clear_lines(lines: int) -> None:
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


def get_artwork(link: str, path: str, types: list) -> None:
    """
    take link of artwork and download them
    path of the downloaded file will look like
    ./Covers/{artist}-{album}/{id}.jpg

    :param link: link to the cover art
    :param path: path where cover art is saved
    :param types: type of art that is saved
    """

    head = f"{' '*5}[{join(types)}] {path.split('/')[-1]}  "

    if os.path.exists(path):
        print(f"{head}{ylw}skipping, file exists{wht}")
    elif args.dry_run:
        print(f"{head}{ylw}skipping, dry run{wht}")
    else:
        # size: str = mbz_api.get_size(link)
        print(f"{head}{ylw}downloading…{wht}")
        mbz_api.save(link, path)
        clear_lines(1)
        print(f"{head}{grn}done{wht}")


def process_releases(releases: list, folder: str) -> None:
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
        release_data: dict = mbz_api.release_art(release_mbid)

        print(f"[{ylw}{index}{wht}] {release_mbid}")

        if not release_data.get('error'):
            for image in release_data['images']:
                link: str = image.get('image')
                name: str = f"{index}-{image.get('id')}.{link.split('.')[-1]}"
                path: str = os.path.join(Config.out_path, folder, name)
                types: list = image.get('types')

                if Config.image_filter == "all":
                    get_artwork(link, path, types)
                elif Config.image_filter.title() in types:
                    get_artwork(link, path, types)

        elif "No cover art found" in release_data['response'].text:
            print(f"     {red}no images{wht}")
        else:
            print(f"     {red}unknown error{wht}")


def auto_pick(rgs: list[dict]) -> dict:
    """
    sorts the list by comparing the scores
    caclulated by the number of releases and score from api
    returns the release-group with highest score

    :param rgs: short for release_groups
    """
    return sorted(rgs, 
            reverse=True,
            key=lambda rg: rg['score']*len(rg['releases']))[0]


def manual_pick(rgs: list) -> dict:
    """
    prints all the results for user to select
    clears the results after selection
    returns the selected release-group

    :param rgs: short for release_groups
    """
    for n, rg in enumerate(rgs, start=1):
        artists: list = [name['name'] for name in rg['artist-credit']]
        artist: str = join(artists)
        p_type: str = rg.get('primary-type', 'none')
        s_type: list = rg.get('secondary-types', [])
        releases: list = rg.get('releases', 'none')
        type_str: str = f"{p_type}, {join(s_type)}" if s_type else p_type

        print(f"[{ylw}{n}{wht}] [{type_str}] ({len(releases)} releases)")
        print(f"{blu}{artist} - {rg.get('title')}{wht}\n")

    print(f"{ylw}0{wht} → exit, {ylw}1..{len(rgs)}{wht} → select, {ylw}none{wht} → auto-select")
    index = input(f"{grn}>choose release-group: {wht}")

    # clearing screen when done, remove if escape code isnt supported
    clear_lines(len(rgs)*3 + 2)

    if index == "0":
        sys.exit(f"{red}exiting...{wht}")

    return auto_pick(rgs) if index == "" else rgs[int(index)-1]


def search_rg(query: str, limit: int) -> tuple[list, str]:
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
    checker = lambda rgs: rgs.get('primary-type') and \
            rgs.get('primary-type').lower() == Config.search_filter

    if Config.search_filter == "all":
        rgs: list = release_groups
    else:
        rgs: list = list(filter(checker, release_groups))

    if not rgs:  # checks if the rgs list is empty
        sys.exit(f"{red}no releases found{wht}")

    release_group: dict = auto_pick(rgs) if Config.auto_select else manual_pick(rgs)

    artist: str = release_group['artist-credit'][0]['name']
    album: str = release_group['title']
    name: str = f"{artist} - {album}"
    releases: list = release_group['releases']

    # removing any illegal character from name
    for illegal_char in '/\\:*?"<>':
        name = name.replace(illegal_char, '')

    name_path = os.path.join(Config.out_path, name)
    if not os.path.exists(name_path) and not args.dry_run:
        os.mkdir(name_path)

    print(name, f"releases: {len(releases)}",
          f"mbid: {release_group['id']}", "—"*42, sep='\n')

    return releases, name


def get_args() -> argparse.Namespace:
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
    parser.add_argument("-v", "--version",
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
        type=str,
        default=Config.image_filter,
        metavar="TYPE",
        choices=["all", "front", "back", "booklet", "obi", "medium"])
    parser.add_argument("-fs", "--filter-search",
        help="filter search results",
        type=str,
        default=Config.search_filter,
        metavar="TYPE",
        choices=["all", "album", "single", "ep", "broadcast", "other"])
    parser.add_argument("-fq", "--filter-quality",
        help="filter image quality",
        type=int,
        default=Config.quality,
        metavar="PX",
        choices=range(100, 2100, 100))

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    join = lambda items: ", ".join([str(item) for item in items])

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

    # logging.basicConfig(level=logging.DEBUG, format="")

    releases, folder = search_rg(args.query, Config.search_limit)
    try:
        process_releases(releases, folder)
    except KeyboardInterrupt:
        sys.exit(f"   {red}keyboard interrupt{wht}")
