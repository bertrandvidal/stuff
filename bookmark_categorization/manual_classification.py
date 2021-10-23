#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from typing import List

with open(os.path.abspath(os.path.expanduser(sys.argv[1]))) as f:
    data = json.load(f)

bookmarks = None
bookmark_path = os.path.join(os.path.curdir, 'bookmarks.json')
if len(sys.argv) == 3:
    bookmark_path = sys.argv[2]

bookmark_path = os.path.abspath(os.path.expanduser(bookmark_path))

if os.path.isfile(bookmark_path):
    with open(bookmark_path) as f:
        bookmarks = json.load(f)

CREATE_NEW_CATEGORY = 'n'
ADD_TO_CATEGORY = 'a'
BACK_UP = 'b'
PRINT_BOOKMARKS = 'p'
commands = [CREATE_NEW_CATEGORY, ADD_TO_CATEGORY, PRINT_BOOKMARKS, BACK_UP]
prompt = """
n: create new category
a: add to current category
b: go back one level
p: print categories
"""


class BookmarkNode:
    name: str
    parent: BookmarkNode
    links: List[str]
    children: List[BookmarkNode]

    def __init__(self, name: str, parent: BookmarkNode = None, links: List[str] = None) -> None:
        self.name = name
        self.parent = parent
        if parent:
            self.parent.children.append(self)
        self.links = links or []
        self.children = []

    def add_link(self, link: str) -> BookmarkNode:
        self.links.append(link)
        return self

    def to_json(self):
        return {
            'name': self.name,
            'links': self.links,
            'children': [child.to_json() for child in self.children]
        }


def print_bookmarks(node: BookmarkNode, depth: int = 0) -> str:
    print((' ' * depth), "- ", node.name, sep='')
    for link in node.links:
        print((' ' * depth), " > ", link, sep='')
    for child in node.children:
        print_bookmarks(child, depth + 1)


def print_bread_crumbs(node: BookmarkNode) -> str:
    components = []
    while node is not None:
        components.append(node.name)
        node = node.parent
    return " > ".join(reversed(components))


def categorize_bookmarks(root: BookmarkNode) -> None:
    for link, topics in data.items():
        choice = None
        current_node = root
        while choice != 'a':
            while choice not in commands:
                print(print_bread_crumbs(current_node))
                children_names = [(i, c.name) for (i, c) in enumerate(current_node.children)]
                print(f"{children_names}")
                print(f"> {link} \n{topics}")
                sub_category_selected = False
                choice = input(prompt)

                try:
                    if int(choice) <= len(current_node.children):
                        current_node = current_node.children[int(choice)]
                        sub_category_selected = True
                except ValueError:
                    pass

                if choice == CREATE_NEW_CATEGORY:
                    new_category_name = input("new category: ")
                    new_category = BookmarkNode(new_category_name, current_node)
                    current_node = new_category
                elif choice == BACK_UP:
                    current_node = current_node.parent or current_node
                elif choice == PRINT_BOOKMARKS:
                    print_bookmarks(root)

                if choice in [CREATE_NEW_CATEGORY, ADD_TO_CATEGORY, BACK_UP] or sub_category_selected:
                    print("\033c")  # clear screen
                if choice != ADD_TO_CATEGORY:
                    choice = None
        if choice == ADD_TO_CATEGORY:
            current_node.add_link(link)


root = BookmarkNode("root", None)

if bookmarks:
    pass

try:
    categorize_bookmarks(root)
except KeyboardInterrupt:
    with open(bookmark_path, 'w') as f:
        json.dump(root.to_json(), f)
