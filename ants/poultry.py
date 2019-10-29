from collections import Counter
from itertools import permutations
from hashlib import md5


class PoultryAndAnts:
    """
    See http://followthewhiterabbit.trustpilot.com/cs/step3.html
    """

    def __init__(self, anagram, targets):
        """
        :param anagram: anagram that we are looking for
        :param targets: list of md5s of anagrams that would match the given
        anagram
        """
        self.anagram_counter = Counter(anagram)
        self.anagram_length = len(anagram)
        self.targets = targets

    def find_match(self, node):
        """ Given a fully built tree return the first anagram found that has
        an md5 found in self.targets. Recursive method visiting the given
        node first then its children in order they were added.

        :param node: the node being visited
        :return: the first found list of words that have an md5 found in
        self.targets, None if no such list of words can be found
        """
        (words, length, _, children) = node
        # we've reached a leaf node that has the right amount of letters
        if not children and length == self.anagram_length:
            # check for md5 of all permutations with white spaces
            for perm in permutations(words):
                digest = md5(" ".join(perm)).hexdigest()
                if digest in self.targets:
                    return list(perm)
        for child in children:
            self.find_match(child)

    def nb_leaf_nodes(self, node):
        """ Informational method to get the number of leaf nodes that can be
        reached from the given node. Recursive method.

        :param node: node being visited
        :return: number of leaf nodes that can be reached from the given node
        """
        (_, __, ___, children) = node
        if not children:
            return 1
        leaves = 0
        for c in children:
            leaves += self.nb_leaf_nodes(c)
        return leaves

    def add_node(self, node, new_word, new_word_counter):
        """ Add 'new_word' to the given node and to any of its children if
        'word_contains' returns true.

        :param node: current node that should get 'new_word' added to
        :param new_word: the word to add to the current node
        :param new_word_counter: the Counter from 'new_word'
        :return: None
        """
        (words, length, counter, children) = node
        for c in children:
            self.add_node(c, new_word, new_word_counter)
        new_node_counter = new_word_counter + counter
        if self.word_contains(new_node_counter, self.anagram_counter):
            children.append(
                (words + [new_word], length + len(new_word), new_node_counter, []))

    def word_contains(self, needle, haystack):
        """ Check whether or not the needle (Counter of a node) can be
        fit in haystack (Counter of anagram). A Counter is said to fit within
        another Counter if for common letters the haystack has more occurrences.

        :param needle: Counter of a single word
        :param haystack: Counter of the anagram
        :return: true if the needle fit in the haystack
        """
        return all(haystack[k] - v >= 0 for k, v in needle.items())

    def build_tree(self, words):
        """ Build a tree of nodes that only contain letter from the anagram
        and each letter will appear no more times that it does in the anagram

        Node: ([words], sum length of [words], Counter([words]), [children])

        TODO: output should not be mingled with the logic

        :param words: the word list to use to find an anagram
        :return: the original node that was passed in
        """
        node = ([], 0, Counter(), [])
        i = 0
        for word in set(words):
            try:
                # If all letters of the word are in the anagram
                word_counter = Counter(word)
                if self.word_contains(word_counter, self.anagram_counter):
                    self.add_node(node, word, word_counter)
                i += 1
                if i % 1000 == 0:
                    print "done: ", i
                    if i % 5000 == 0:
                        print "nb-leaves: %d" % self.nb_leaf_nodes(node)
            except KeyboardInterrupt as e:
                break

        return node


if __name__ == "__main__":

    with open("./md5.txt", "r") as f:
        target_md5 = [l.strip("\n") for l in f]

    with open("./words.txt", "r") as f:
        wordlist = [line.strip("\n") for line in f]

    with open("./anagram.txt", "r") as f:
        anagram_text = f.readline().strip("\n")

    ants = PoultryAndAnts(anagram_text, target_md5)
    print "Looking for %s: %s" % (anagram_text, ants.anagram_counter)
    tree = ants.build_tree(wordlist)
    print "total nb-leaves: %d" % ants.nb_leaf_nodes(tree)
    ants.find_match(tree)
