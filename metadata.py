#!/usr/bin/env python3

"""
DESCRIPTION
"""

__version__ = "1.0"


import os
import sys
import json
import argparse
import musicbrainz_api as mbz


red = "\33[31m"
grn = "\33[32m"
ylw = "\33[33m"
blu = "\33[36m"
wht = "\33[00m"

pretty = lambda resp: json.dumps(resp, indent=2)
join = lambda items: ", ".join([str(item) for item in items])

def process_ar(mbid: str):
    response: dict = mbz.browse_release_group(link="artist", mbid=mbid)
    print(pretty(response))
    # print(len(response['release-groups']))
    # print(pretty(response['release-groups']))

def search_ar(query: str, limit: int=5) -> dict:
    """
    docstring
    """
    response: dict = mbz.search_artist(query, limit, 0)
    results: list = response['artists']
    # print(pretty(results))

    print(f"{response.get('count')} results {len(results)} shown")

    n = 0
    for n, result in enumerate(results, start=1):
        name: str = result.get('name')
        type: str = result.get('type')
        id: str = result.get('id')
        # tags: str = result.get('tags', [])
        tags = join([item['name'] for item in result.get('tags', [])])
        score: int = result.get('score')
        country: str = result.get('country', 'NA')

        print(f"[{ylw}{n}{wht}] {tags}")
        print(f"    {blu}{name}{wht}")

    # print(results[0])
    index = int(input(f"{grn}>choose artist: {wht}"))

    if index == 0:
        sys.exit(f"{red}exiting...{wht}")
    else:
        print(pretty(results[index-1]))
        return results[index-1]


def get_args():
    """
    docstring
    """
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("artist",
        help="name of the artist")
    parser.add_argument("-l", "--limit",
        help="flag help",
        default=5)
    parser.add_argument("-v", "--verbose",
        help="change logging level to debug",
        action="store_true")
    parser.add_argument("-V", "--version",
        help="show version and exit",
        action="version",
        version=__version__)

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    artist: dict = search_ar(args.artist, args.limit)
    process_ar(artist['id'])
