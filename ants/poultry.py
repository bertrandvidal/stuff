from collections import Counter

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


for word in set(wordslist):
    # If all letters of the word are in the anagram
    if not set(word).difference(anagram_letters):
        add_node(root, word)


def nb_leaf_nodes(node, nb_leaves):
    (_, __, ___, children) = node
    if not children:
        return 1
    r = 0
    for c in children:
        r += nb_leaf_nodes(c, nb_leaves)
    return nb_leaves + r


print "%s:%s" % (anagram, anagram_length)

print format_tree(root,
                  format_node=lambda x: "-".join(_ for _ in x[0]) + ":" +
                                        str(x[1]) + ":%s" % (
                      str(x[2]) if not x[3] else ""),
                  get_children=lambda x: x[3])

print "nb-leaves: %d" % nb_leaf_nodes(root, 0)
