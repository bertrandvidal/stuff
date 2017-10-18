from hashlib import md5
from collections import Counter
from pprint import pprint
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

root = ([], 0, Counter(), [])

print "Looking for %s" % anagram

def add_node(node, new_word):
    (words, length, counter, children) = node
    l = len(new_word)
    for c in children:
        if set(c[0]).difference(anagram_letters):
            print "Skipping %s" % c[0]
            return
        add_node(c, new_word)
    new_node_length = length + l
    if new_node_length <= anagram_length:
        children.append((words + [new_word], new_node_length, None, []))

for w in wordslist[:10]:
    add_node(root, w)


def nb_leaf_nodes(node, nb_leaves):
    (_, __, ___, children) = node
    if not children:
        return 1
    r = 0
    for c in children:
        r += nb_leaf_nodes(c, nb_leaves)
    return nb_leaves + r


def compute_permutations(node):
    (words, _, __, children) = node
    if not children:
        print "Checking for: %s" % words
    for c in children:
        compute_permutations(c)


print "%s:%s" % (anagram, anagram_length)

print format_tree(root,
                  format_node=lambda x: "-".join(_ for _ in x[0]) + ":" +
                  str(x[1]) + ":%s" % (str(x[2]) if not x[3] else ""),
                  get_children=lambda x: x[3])


print "nb-leaves: %d" % nb_leaf_nodes(root, 0)

