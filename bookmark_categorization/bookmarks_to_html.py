#!/usr/bin/env python3
import json
import os
import sys
from typing import Dict, List

from bs4 import BeautifulSoup

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


def create_bookmark_tag(attributes: Dict, contents: str) -> str:
    return f'<DT><A HREF="{attributes["HREF"]}" ICON="{attributes.get("ICON", "")}" ADD_DATE="{attributes["ADD_DATE"]}">{contents}</A>'


def create_folder_tag(folder: Dict) -> List[str]:
    print(f"Handling folder {folder['name']}")
    content = [f'<DT><H3 ADD_DATE="1554239916" LAST_MODIFIED="1620574779">{folder["name"]}</H3>',
               '<DL><p>']

    for sub_folder in folder['children']:
        content.extend(create_folder_tag(sub_folder))

    for link in folder['links']:
        (attributes, contents) = LINKS[link]
        content.append(create_bookmark_tag(attributes, contents))
    content.append('</DL><p>')

    return content


html_content: list[str] = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>""".split('\n')

with open(os.path.abspath(bookmark_file)) as f:
    html_content.extend(create_folder_tag(json.load(f)))

html_content.append("</DL><p>")

print(len(html_content))

with open(os.path.expanduser("~/Documents/bert.html"), "w") as f:
    f.writelines([l + "\n" for l in html_content])
