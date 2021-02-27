import unittest

from grammar import GrammarGenerator, Grammar
from pixel import Pixel


class GrammarGeneratorTest(unittest.TestCase):
    _identity_grammar = Grammar(rules=[lambda p: [p]])
    _duplicate_grammar = Grammar(rules=[lambda p: [p, p]])
    _next_diagonal_grammar = Grammar(rules=[lambda p: [p, Pixel(x=p.x + 1, y=p.y + 1)]])

    def test_nb_iteration(self):
        generator = GrammarGenerator(grammar=self._identity_grammar, start=Pixel())
        self.assertEqual(len(list(generator.generate(12))), 12)

    def test_generation_without_duplication(self):
        generator = GrammarGenerator(grammar=self._duplicate_grammar, start=Pixel())
        for iteration in generator.generate(5):
            self.assertEqual(len(iteration), 1)

    def test_existing_pixels_are_retained(self):
        n = 10
        generator = GrammarGenerator(grammar=self._next_diagonal_grammar, start=Pixel())
        # n + 1 because the n iteration add element to start so: n + start
        self.assertEqual(len(list(generator.generate(n))[-1]), n + 1)


if __name__ == '__main__':
    unittest.main()
