import unittest
from collections import Counter
from hashlib import md5

from poultry import PoultryAndAnts


class PoultryAndAntsTest(unittest.TestCase):

    def test_word_contains_with_empty_counters(self):
        self.assertTrue(
            PoultryAndAnts("", []).word_contains(Counter(), Counter()))

    def test_word_contains_with_needle_empty_counter(self):
        self.assertTrue(
            PoultryAndAnts("", []).word_contains(Counter(), Counter("a")))

    def test_word_contains_with_haystack_empty_counter(self):
        self.assertFalse(
            PoultryAndAnts("", []).word_contains(Counter("a"), Counter()))

    def test_word_contains_with_needle_equal_to_haystack(self):
        self.assertTrue(
            PoultryAndAnts("", []).word_contains(Counter("a"), Counter("a")))

    def test_word_contains_with_needle_contained_in_haystack(self):
        self.assertTrue(
            PoultryAndAnts("", []).word_contains(Counter("test"),
                                                 Counter("this is a test")))

    def test_word_contains_with_needle_not_contained_in_haystack(self):
        self.assertFalse(
            PoultryAndAnts("", []).word_contains(Counter("test"),
                                                 Counter("word")))

    def test_word_contains_with_needle_has_one_too_many_letter(self):
        self.assertFalse(
            PoultryAndAnts("", []).word_contains(Counter("abc"),
                                                 Counter("ab")))

    def test_word_contains_with_needle_has_one_too_many_letter_occurrence(self):
        self.assertFalse(
            PoultryAndAnts("", []).word_contains(Counter("aba"),
                                                 Counter("ab")))

    def test_nb_leaf_nodes_empty_tree(self):
        nodes = PoultryAndAnts("", []).nb_leaf_nodes((None, None, None, []))
        self.assertEqual(nodes, 1)

    def test_nb_leaf_nodes_with_one_level(self):
        children = [(None, None, None, []) for _ in [1, 2, 3]]
        nodes = PoultryAndAnts("", []).nb_leaf_nodes(
            (None, None, None, children))
        self.assertEqual(nodes, len(children))

    def test_nb_leaf_nodes_with_multiple_level(self):
        child_1 = (None, None, None, [(None, None, None, []) for _ in range(3)])
        nodes = PoultryAndAnts("", []).nb_leaf_nodes(
            (None, None, None, [child_1, child_1]))
        self.assertEqual(nodes, 6)

    def _print_tree(self, node, indent):
        (words, _, counter, children) = node
        print '  ' * indent, words, ' -- ', counter, ': ', len(children)
        for c in children:
            self._print_tree(c, indent + 1)

    def test_build_tree_structure(self):
        ants = PoultryAndAnts("ac", [])
        tree = ants.build_tree(["a", "b", "c", "d"])
        self.assertEqual(ants.nb_leaf_nodes(tree), 2)

        ac_node = (["a", "c"], 2, Counter("ac"), [])
        a_node = (["a"], 1, Counter("a"), [ac_node])
        c_node = (["c"], 1, Counter("c"), [])
        expected_tree = ([], 0, Counter(), [a_node, c_node])
        self.assertEqual(tree, expected_tree)

    def test_add_node_top_node(self):
        ants = PoultryAndAnts("abc", [])
        node = ([], 1, Counter(), [])
        ants.add_node(node, "a", Counter("a"))
        nb_nodes = ants.nb_leaf_nodes(node)
        self.assertEqual(nb_nodes, 1)

    def test_add_node_not_part_of_anagram(self):
        ants = PoultryAndAnts("abc", [])
        node = ([], 1, Counter(), [])
        ants.add_node(node, "d", Counter("d"))
        nb_nodes = ants.nb_leaf_nodes(node)
        self.assertEqual(nb_nodes, 1)  # the root node is also a leaf

    def test_add_node_all_letters(self):
        ants = PoultryAndAnts("abc", [])
        node = ([], 1, Counter(), [])
        ants.add_node(node, "a", Counter("a"))
        ants.add_node(node, "b", Counter("b"))
        ants.add_node(node, "c", Counter("c"))
        nb_nodes = ants.nb_leaf_nodes(node)
        self.assertEqual(nb_nodes, 4)

    def test_build_tree(self):
        ants = PoultryAndAnts("abc", [])
        nodes = ants.build_tree(["a", "b", "c", "d"])
        nb_nodes = ants.nb_leaf_nodes(nodes)
        self.assertEqual(nb_nodes, 4)

    def test_build_tree_not_part_of_anagram(self):
        ants = PoultryAndAnts("abc", [])
        nodes = ants.build_tree(["d", "e"])
        nb_nodes = ants.nb_leaf_nodes(nodes)
        self.assertEqual(nb_nodes, 1) # the root node is also a leaf

    def test_find_match(self):
        ants = PoultryAndAnts("ab", [md5("b a").hexdigest()])
        nodes = ants.build_tree(["a", "b", "c", "d"])
        match = ants.find_match(nodes)
        self.assertEqual(match, ["b", "a"])

    def test_find_match_no_match(self):
        ants = PoultryAndAnts("ab", [md5("b a").hexdigest()])
        nodes = ants.build_tree(["c", "d"])
        match = ants.find_match(nodes)
        self.assertIsNone(match)


if __name__ == '__main__':
    unittest.main()
