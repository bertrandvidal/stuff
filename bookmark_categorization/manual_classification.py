#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from typing import List, Dict

with open(os.path.abspath(os.path.expanduser(sys.argv[1]))) as f:
    link_categorization = json.load(f)

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
a: add to current category [%s]
b: go back one level [%s]
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

    @staticmethod
    def from_json(json_payload: dict, parent: BookmarkNode = None) -> BookmarkNode:
        node = BookmarkNode(json_payload['name'], parent, json_payload['links'])
        for children_payload in json_payload['children']:
            BookmarkNode.from_json(children_payload, node)
        return node


def print_bookmarks(node: BookmarkNode, depth: int = 0):
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


def get_already_processed_links(node: BookmarkNode, accumulator: List[str] = None) -> List[str]:
    accumulator = accumulator or []
    for child in node.children:
        accumulator.extend(get_already_processed_links(child, accumulator))
    accumulator.extend(node.links)
    return accumulator


def categorize_bookmarks(root_node: BookmarkNode, links: Dict[str, Dict]) -> None:
    already_processed_links = get_already_processed_links(root_node)
    for link, topics in links.items():
        if link in already_processed_links:
            continue
        choice = None
        current_node = root_node
        while choice != ADD_TO_CATEGORY:
            while choice not in commands:
                print(print_bread_crumbs(current_node))
                children_names = [(i, c.name) for (i, c) in enumerate(current_node.children)]
                print(f"{children_names}")
                print(f"> {link} \n{topics}")
                sub_category_selected = False
                choice = input(prompt % (current_node.name, current_node.parent.name if current_node.parent else None))

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
                    print_bookmarks(root_node)

                if choice in [CREATE_NEW_CATEGORY, ADD_TO_CATEGORY, BACK_UP] or sub_category_selected:
                    print("\033c")  # clear screen
                if choice != ADD_TO_CATEGORY:
                    choice = None
        if choice == ADD_TO_CATEGORY:
            current_node.add_link(link)


root = BookmarkNode("root", None)

if bookmarks:
    root = BookmarkNode.from_json(bookmarks)

try:
    categorize_bookmarks(root, link_categorization)
except KeyboardInterrupt:
    with open(bookmark_path, 'w') as f:
        json.dump(root.to_json(), f)
