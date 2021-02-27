import unittest

from grammar import GrammarGenerator, Grammar
from pixel import Pixel


class GrammarGeneratorTest(unittest.TestCase):
    _identity_grammar = Grammar(rules=[lambda p: [p]])
    _duplicate_grammar = Grammar(rules=[lambda p: [p, p]])

    def test_nb_iteration(self):
        generator = GrammarGenerator(grammar=self._identity_grammar, start=Pixel())
        self.assertEqual(len(list(generator.generate(12))), 12)

    def test_generation_without_duplication(self):
        generator = GrammarGenerator(grammar=self._duplicate_grammar, start=Pixel())
        for iteration in generator.generate(5):
            self.assertEqual(len(iteration), 1)


if __name__ == '__main__':
    unittest.main()
