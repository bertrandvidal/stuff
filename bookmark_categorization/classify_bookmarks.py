#!/usr/bin/env python3

import sys
import os
import bs4
import json
import textrazor

bookmark_file = sys.argv[1]

# extract all href from bookmark file
with open(os.path.abspath(os.path.expanduser(bookmark_file))) as f:
    cleaned_up_lines = [line.strip("\n ") for line in f.readlines()]
    soup = bs4.BeautifulSoup(" ".join(cleaned_up_lines), 'html.parser')
    links = [link.attrs['href'] for link in soup.find_all('a')]

link_topics = {}

api_client = textrazor.TextRazor(os.environ['TEXTRAZOR_API_KEY'],
                                 extractors=['topics'])
api_client.set_cleanup_use_metadata(True)
api_client.set_cleanup_mode('stripTags')

for link in links:
    response = api_client.analyze_url(link)
    link_topics[link] = {t.label: t.score for t in
                         sorted(response.topics(),
                                key=lambda x: x.score,
                                reverse=True)[:10]}

with open("output.json", "w") as f:
    json.dump(link_topics, f)

