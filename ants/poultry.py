from collections import Counter
from itertools import permutations
from hashlib import md5


wordslist = []
anagram = None
target_md5 = None

with open("./words.txt", "r") as f:
    wordslist = [line.strip("\n") for line in f]

with open("./anagram.txt", "r") as f:
    anagram = f.readline().strip("\n")

with open("./md5.txt", "r") as f:
    target_md5 = [l.strip("\n") for l in f]

anagram_counter = Counter(anagram)
anagram_length = len(anagram)
anagram_letters = set(anagram)


def word_contains(needle, haystack):
    return all(haystack[k] - v >= 0 for k,v in needle.items())


def add_node(node, new_word, new_word_counter):
    (words, length, counter, children) = node
    for c in children:
        add_node(c, new_word, new_word_counter)
    l = len(new_word)
    new_node_length = length + l
    new_node_counter = new_word_counter + counter
    if word_contains(new_node_counter, anagram_counter):
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
            if digest in target_md5:
                print "\n\nWINNER!! - %s \n\n" % list(perm)
    for child in children:
        find_match(child)


root = ([], 0, Counter(), [])

print "Looking for %s: %s" % (anagram, anagram_counter)

i = 0
for word in set(wordslist):
    try:
        # If all letters of the word are in the anagram
        word_counter = Counter(word)
        if word_contains(word_counter, anagram_counter):
            add_node(root, word, word_counter)
        i += 1
        if i % 1000 == 0:
            print "done: ", i
            if i % 5000 == 0:
                print "nb-leaves: %d" % nb_leaf_nodes(root, 0)
    except KeyboardInterrupt as e:
        break

print "%s:%s" % (anagram, anagram_length)
print "nb-leaves: %d" % nb_leaf_nodes(root, 0)

find_match(root)
