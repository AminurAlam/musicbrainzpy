#!/usr/bin/env python3

"""
Musicbrainz artwork downloader
start by searching for an album and select it
it'll get all the results and downloads them one by one

importaint links:
    https://github.com/AminurAlam/musicbrainzpy
    https://musicbrainz.org/doc/MusicBrainz_API
    https://musicbrainz.org/doc/MusicBrainz_API/Search
    https://musicbrainz.org/doc/MusicBrainz_Database/Schema
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
    auto_select = False     # automatically select the search result
    quality = 0             # quality of image to be downloaded


def clear_lines(lines: int) -> None:
    """
    clears lines from terminal

    :param lines: number of lines to be cleared
    """
    for _ in range(lines):
        sys.stdout.write('\x1b[1A')  # escape code to move cursor up
        sys.stdout.write('\x1b[2K')  # escape code to clear line
    sys.stdout.flush()


def get_artwork(link: str, path: str, types: list[str]) -> None:
    """
    take link of artwork and download them
    path of the downloaded file will look like
    ./Covers/{artist}-{album}/{id}.jpg

    :param link: link to the cover art
    :param path: path where cover art is saved
    :param types: type of art that is saved
    """
    if os.path.exists(path):
        print(f"     {ylw}[!]{wht} skipping, file exists [{join(types)}]")
    elif args.dry_run:
        print(f"     {ylw}[!]{wht} skipping, dry run [{join(types)}]")
    else:
        # size: str = mbz_api.get_size(link)
        print(f"     {ylw}[…]{wht} downloading [{join(types)}]")
        mbz_api.save(link, path)
        clear_lines(1)
        print(f"     {grn}[✓]{wht} [{join(types)}]")


def process_releases(releases: list[dict], folder_name: str) -> None:
    """
    takes releases from search reasults
    then gets links of releases from caa
    doesn't print traceback on KeyboardInterrupt

    :param releases: list containing mbid of releases
    :param folder_name: path of folder where files are downloaded
    """
    for n, release in enumerate(releases, start=1):
        release_mbid: str = release['id']
        release_data: dict = mbz_api.release_art(release_mbid)

        print(f"[{ylw}{n:02d}{wht}] {release_mbid}")

        if not release_data.get('error'):
            for image in release_data['images']:
                link: str = image.get('image')  # TODO
                file: str = f"{n:02d}-{image['id']}.{link.split('.')[-1]}"
                file_name: str = os.path.join(folder_name, file)
                types: list = image.get('types')

                if Config.image_filter == "all":
                    get_artwork(link, file_name, types)
                elif Config.image_filter.title() in types:
                    get_artwork(link, file_name, types)

        elif "No cover art found" in release_data['response'].text:
            print(f"     {red}[✗]{wht} no images")
        else:
            print(f"     {red}[✗]{wht} unknown error")


def pick(rgs: list[dict]) -> dict:
    """
    prints all the results for user to select
    clears the results after selection
    returns the selected release-group

    :param rgs: short for release-groups
    """
    rgs.sort(reverse=True, key=lambda rg: rg['score']*len(rg['releases']))

    if Config.auto_select:
        return rgs[0]

    for n, rg in enumerate(rgs, start=1):
        artists: str = join([name['name'] for name in rg['artist-credit']])
        types_list: list = rg.get('secondary-types', [])
        types_list.insert(0, rg.get('primary-type', 'none'))
        types_str: str = join(types_list)

        print(f"[{ylw}{n}{wht}] [{types_str}] ({rg['count']} releases)")
        print(f"{blu}{artists} - {rg.get('title')}{wht}\n")

    choice: str = input(f"{grn}>choose release-group: {wht}")
    clear_lines(len(rgs)*3 + 1)

    if choice == "0":
        sys.exit(f"{red}exiting…{wht}")
    if choice == "":
        return rgs[0]
    else:
        return rgs[int(choice)-1]


def search_rg(query: str, limit: int) -> tuple[list, str]:
    """
    shows release-groups (rgs) related to query
    from which picks a release-group (rg) to download

    :param query:
    :param limit:
    """

    response: dict = mbz_api.search_release_group(query, limit, 0)
    rgs: list[dict] = response['release-groups']

    # filtering the search results we got using -fs / --filter-search
    if Config.search_filter != "all":
        checker = lambda rgs: rgs.get('primary-type') and \
                    rgs.get('primary-type').lower() == Config.search_filter
        rgs = list(filter(checker, rgs))
        if not rgs:  # exits if everything gets filtered
            sys.exit(f"{red}try changing filter, or increasing limit{wht}")

    rg: dict = pick(rgs)  # gets the appropriate release-group from release-groups

    name: str = rg['artist-credit'][0]['name']+' - '+rg['title']
    for illegal_char in r':?"[|]\<*>/':
        name = name.replace(illegal_char, '')
    folder_name = os.path.join(Config.out_path, name)
    if not os.path.exists(folder_name) and not args.dry_run:
        os.makedirs(folder_name)

    print(name, f"releases: {rg['count']}", f"mbid: {rg['id']}",
          "—"*42, sep='\n')

    return rg['releases'], folder_name


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
        version=f"MusicBrainzPy v{__version__}\n"
                f"MusicBrainz_API v{mbz_api.__version__}\n"
                f"requests v{mbz_api.requests.__version__}\n"
                f"Python v{sys.version.split()[0]}")
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
        metavar="TYPE",
        default=Config.image_filter,
        choices=["all", "front", "back", "booklet", "obi", "medium"])
    parser.add_argument("-fs", "--filter-search",
        help="filter search results",
        type=str,
        metavar="TYPE",
        default=Config.search_filter,
        choices=["all", "album", "single", "ep", "broadcast", "other"])
    parser.add_argument("-fq", "--filter-quality",
        help="filter image quality",
        type=int,
        metavar="PX",
        default=Config.quality,
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
    red = "\033[31m" if color else ""
    grn = "\033[32m" if color else ""
    ylw = "\033[33m" if color else ""
    blu = "\033[36m" if color else ""
    wht = "\033[00m" if color else ""
    bld = "\033[01m" if color else ""
    gry = "\033[02m" if color else ""
    itl = "\033[03m" if color else ""
    und = "\033[04m" if color else ""

    # logging.basicConfig(level=logging.DEBUG, format="")
    # for k, v in args.__dict__.items(): print(f"  {k}: {v}")

    releases, folder_name = search_rg(args.query, Config.search_limit)

    try:
        process_releases(releases, folder_name)
    except KeyboardInterrupt:
        sys.exit(f"   {red}keyboard interrupt{wht}")
