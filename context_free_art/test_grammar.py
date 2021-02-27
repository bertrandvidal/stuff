import unittest

from grammar import GrammarGenerator, Grammar
from pixel import Pixel


class GrammarGeneratorTest(unittest.TestCase):

    def test_nb_iteration(self):
        generator = GrammarGenerator(grammar=Grammar(rules=[lambda p: [p]]), start=Pixel())
        self.assertEqual(len(list(generator.generate(12))), 12)


if __name__ == '__main__':
    unittest.main()
