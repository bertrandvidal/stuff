import unittest
from collections import Counter

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


if __name__ == '__main__':
    unittest.main()
