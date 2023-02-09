"""
DESCRIPTION
"""

__version__ = "1.0"


import sys
import json
import argparse
import musicbrainz_api as mbz


def process_ar(mbid: str):
    response: dict = mbz.lookup("artist", mbid=mbid, inc="release-groups")

    print(pretty(response))
    print(len(response['release-groups']))
    # print(pretty(response['release-groups']))

def search_ar(query: str, limit: int=5) -> str:
    """
    docstring
    """
    response: dict = mbz.search("artist", query, limit, 0)
    results: list = response['artists']
    # print(pretty(results))

    print(f"{response.get('count')} results {len(results)} shown")

    n = 0
    for n, result in enumerate(results, start=1):
        name: str = result.get('name')
        # type: str = result.get('type')
        # id: str = result.get('id')
        # tags: str = result.get('tags', [])
        # tags = join([item['name'] for item in result.get('tags', [])])
        # score: int = result.get('score')
        # country: str = result.get('country', 'NA')

        print(f"[{ylw}{n}{wht}] {name}{wht}")

    # print(results[0])
    index = int(input(f"{grn}>choose artist: {wht}"))

    if index == 0:
        sys.exit("exiting...")
    else:
        # print(pretty(results[index-1]))
        return results[index-1]['id']


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("artist",
        help="name of the artist", type=str)
    parser.add_argument("-l", "--limit",
        help="limit the number of results displayed",
        type=int, default=5, metavar="NUM")

    args = parser.parse_args()
    pretty = lambda resp: json.dumps(resp, indent=2)
    join = lambda items: ", ".join([str(item) for item in items])
    grn, ylw, blu, wht = "\33[32m", "\33[33m", "\33[36m", "\33[00m"

    process_ar(search_ar(args.artist, args.limit))
