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


if __name__ == '__main__':
    unittest.main()
