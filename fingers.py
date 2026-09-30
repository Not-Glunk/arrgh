from xml.etree import ElementTree as ET
import urllib.request

from datetime import datetime

def nyaa(search_string):
    """returns a list of dictionaries with search results each containing `title`, `pubDate`, `seeders`, `leechers`, `completed`, `infoHash` and `size`"""
    base_url = "https://nyaa.si/?page=rss&q="

    search_terms = search_string.replace(' ', '+')
    query = base_url + search_terms

    fetched_xml = urllib.request.urlopen(query).read()

    # fetch and parse xml rss feed into a list of dictionaries
    root = ET.fromstring(fetched_xml)
    items = []

    found_results = False
    for item in root.findall("./channel/item"):
        data = {}
        found_results = True
        for child in item:
            tag = child.tag.split("}")[-1]
            data[tag] = child.text.strip() if child.text else None
        items.append(data)

    # compile new stripped and formatted list of dictionaries to return
    parsed_items = []
    for item in items:
        parsed_item = {
            "title": item["title"],
            "pubDate": datetime.strptime(item["pubDate"], "%a, %d %b %Y %H:%M:%S %z").strftime("%a %Y-%m-%d, %H:%M"),
            "seeders": item["seeders"],
            "leechers": item["leechers"],
            "completed": item["downloads"],
            "infoHash": item["infoHash"],
            "size": item["size"],
        }
        parsed_items.append(parsed_item)
    if not found_results:
        return None

    return parsed_items

#####
#
# You can define your indexers! (helper methods can be declared by naming them as `_helper()`)
# just write a function following the below template that takes a search query string as input, and returns a list of dictionaries containing torrent info formatted as follows, and it'll appear for selection!
# ^^ your fault if ya get things wrong
#
###
#
# "title": "Made in Abyss S01"
# "pubDate": "Wed 2026-09-30, 15:37"
# "seeders": 48
# "leechers": 5
# "completed": 420
# "infoHash": ac5463f76633fb3906d4a129e96a766a4b19be7b
# "size": 505.3 MiB
#
#####

# def indexer(search_string):
#    """cool indexer"""
#
#    // your fetching/parsing logic here
#
#    parsed_items = []
#    for item in items:
#        parsed_item = {
#            "title": item["title"],
#            "pubDate": datetime.strptime(item["pubDate"], "%a, %d %b %Y %H:%M:%S %z").strftime("%a %Y-%m-%d, %H:%M"),
#            "seeders": item["seeders"],
#            "leechers": item["leechers"],
#            "completed": item["downloads"],
#            "infoHash": item["infoHash"],
#            "size": item["size"],
#        }
#    parsed_items.append(parsed_item)
#    if not found_results:
#        return None
#
#    return parsed_items
