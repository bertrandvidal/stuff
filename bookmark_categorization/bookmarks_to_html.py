#!/usr/bin/env python3
import json
import os
import sys
from typing import Dict

from bs4 import BeautifulSoup, Tag, NavigableString

bookmark_file = sys.argv[1]
LINKS = {}

# extract all href from bookmark file
with open(os.path.abspath('bookmarks_10_23_21.html')) as f:
    cleaned_up_lines = [line.strip("\n ") for line in f.readlines()]
    soup = BeautifulSoup(" ".join(cleaned_up_lines), 'html.parser')
    LINKS = {
        link.attrs['href']:
            (
                {
                    'ADD_DATE': link.attrs['add_date'],
                    'ICON': link.attrs.get('icon'),
                    'HREF': link.attrs['href'],
                },
                link.contents[0]
            )
        for link in soup.find_all('a')
    }


def create_bookmark_tag(attributes: Dict, contents: str) -> Tag:
    dt = Tag(soup, name='DT')
    a = Tag(soup, name='A', attrs=attributes)
    a.append(NavigableString(contents))
    dt.append(a)
    return dt


def create_folder_tag(folder: Dict) -> Tag:
    dt = Tag(soup, name='DT')
    title = Tag(soup, name='H3', attrs={'ADD_DATE': 1596119447, 'LAST_MODIFIED': 1596119447})
    title.append(NavigableString(folder['name']))
    dt.append(title)
    dl = Tag(soup, name='DL')
    p = Tag(soup, name='p')
    for link in folder['links']:
        (attributes, contents) = LINKS[link]
        p.append(create_bookmark_tag(attributes, contents))

    for sub_folder in folder['children']:
        dl.append(create_folder_tag(sub_folder))
    dl.append(p)
    dt.append(dl)
    return dt


with open(os.path.abspath(bookmark_file)) as f:
    tree = create_folder_tag(json.load(f))

with open(os.path.expanduser("~/Documents/bert.html"), "w") as f:
    f.write(str(tree))
