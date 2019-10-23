from collections import Counter
from itertools import permutations
from hashlib import md5


class PoultryAndAnts:

    def __init__(self, anagram, target):
        self.anagram_counter = Counter(anagram)
        self.anagram_length = len(anagram)
        self.target = target

    def find_match(self, node):
        (words, length, _, children) = node
        # we've reached a leaf node that has the right amount of letters
        if not children and length == self.anagram_length:
            # check for md5 of all permutations with white spaces
            for perm in permutations(words):
                digest = md5(" ".join(perm)).hexdigest()
                if digest in self.target:
                    print "\n\nWINNER!! - %s \n\n" % list(perm)
        for child in children:
            self.find_match(child)

    def nb_leaf_nodes(self, node, nb_leaves):
        (_, __, ___, children) = node
        if not children:
            return 1
        r = 0
        for c in children:
            r += self.nb_leaf_nodes(c, nb_leaves)
        return nb_leaves + r

    def add_node(self, node, new_word, new_word_counter):
        (words, length, counter, children) = node
        for c in children:
            self.add_node(c, new_word, new_word_counter)
        l = len(new_word)
        new_node_length = length + l
        new_node_counter = new_word_counter + counter
        if self.word_contains(new_node_counter, self.anagram_counter):
            children.append(
                (words + [new_word], new_node_length, new_node_counter, []))

    def word_contains(self, needle, haystack):
        return all(haystack[k] - v >= 0 for k,v in needle.items())

    def find_anagram(self, wordlist):
        i = 0
        for word in set(wordlist):
            try:
                # If all letters of the word are in the anagram
                word_counter = Counter(word)
                if self.word_contains(word_counter, self.anagram_counter):
                    self.add_node(root, word, word_counter)
                i += 1
                if i % 1000 == 0:
                    print "done: ", i
                    if i % 5000 == 0:
                        print "nb-leaves: %d" % self.nb_leaf_nodes(root, 0)
            except KeyboardInterrupt as e:
                break

        print "%s:%s" % (anagram, self.anagram_length)
        print "nb-leaves: %d" % ants.nb_leaf_nodes(root, 0)


if __name__ == "__main__":

    with open("./md5.txt", "r") as f:
        target_md5 = [l.strip("\n") for l in f]

    with open("./words.txt", "r") as f:
        wordlist = [line.strip("\n") for line in f]

    with open("./anagram.txt", "r") as f:
        anagram = f.readline().strip("\n")

    root = ([], 0, Counter(), [])
    ants = PoultryAndAnts(anagram, target_md5)
    print "Looking for %s: %s" % (anagram, ants.anagram_counter)
    ants.find_anagram(wordlist)
