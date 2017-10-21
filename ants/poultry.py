from collections import Counter
from itertools import permutations
from hashlib import md5

from tree_format import format_tree

wordslist = []
anagram = None
target_md5 = None

with open("./words.txt", "r") as f:
    wordslist = [line.strip("\n") for line in f]

with open("./anagram.txt", "r") as f:
    anagram = f.readline().strip("\n")

with open("./md5.txt", "r") as f:
    target_md5 = f.readline().strip("\n")

anagram_counter = Counter(anagram)
anagram_length = len(anagram)
anagram_letters = set(anagram)


def add_node(node, new_word):
    (words, length, counter, children) = node
    for c in children:
        add_node(c, new_word)
    l = len(new_word)
    new_node_length = length + l
    new_node_counter = Counter(new_word) + counter
    copy_counter = anagram_counter.copy()
    copy_counter.subtract(new_node_counter)
    if new_node_length <= anagram_length and all(
                    x >= 0 for x in copy_counter.values()):
        children.append((words + [new_word], new_node_length, new_node_counter, []))


def nb_leaf_nodes(node, nb_leaves):
    (_, __, ___, children) = node
    if not children:
        return 1
    r = 0
    for c in children:
        r += nb_leaf_nodes(c, nb_leaves)
    return nb_leaves + r


def find_match(node):
    (words, length, _, children) = node
    # we've reached a leaf node that has the right amount of letters
    if not children and length == anagram_length:
        # check for md5 of all permutations with white spaces
        for perm in permutations(words):
            digest = md5(" ".join(perm)).hexdigest()
            if digest in ["e4820b45d2277f3844eac66c903e84be",
                          "23170acc097c24edb98fc5488ab033fe",
                          "665e5bcb0c20062fe8abaaf4628bb154"]:
                print "\n\nWINNER!! - %s \n\n" % list(perm)
    for child in children:
        find_match(child)


root = ([], 0, Counter(), [])

print "Looking for %s" % anagram

i = 0
for word in set(wordslist):
    # If all letters of the word are in the anagram
    if not set(word).difference(anagram_letters):
        add_node(root, word)
    i += 1
    if i % 1000 == 0:
        print "done: ", i
        if i % 5000 == 0:
            print "nb-leaves: %d" % nb_leaf_nodes(root, 0)

print "%s:%s" % (anagram, anagram_length)

print format_tree(root,
                  format_node=lambda x: "-".join(_ for _ in x[0]) + ":" +
                                        str(x[1]) + ":%s" % (
                      str(x[2]) if not x[3] else ""),
                  get_children=lambda x: x[3])

print "nb-leaves: %d" % nb_leaf_nodes(root, 0)

find_match(root)
