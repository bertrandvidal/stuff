import unittest
from dataclasses import dataclass
from typing import List

from canvas import Canvas
from grammar import GrammarGenerator, Grammar, Rule
from pixel import Pixel


@dataclass
class DummyCanvas(Canvas):
    size: int

    def dimension(self):
        return self.size, self.size

    def display(self, pixels: List[Pixel]):
        pass


class RuleTest(unittest.TestCase):

    def test_rule_default_implementation(self):
        self.assertEqual([Pixel()], Rule()(Pixel(), 1, 1))


class GrammarGeneratorTest(unittest.TestCase):
    _identity_grammar = Grammar(rules=[lambda p, w, h: [p]])
    _duplicate_grammar = Grammar(rules=[lambda p, w, h: [p, p]])
    _next_diagonal_grammar = Grammar(rules=[lambda p, w, h: [p, Pixel(x=p.x + 1, y=p.y + 1)]])

    def test_nb_iteration(self):
        size = 12
        generator = GrammarGenerator(grammar=self._identity_grammar, start=Pixel(), canvas=DummyCanvas(size))
        self.assertEqual(len(list(generator.generate(size))), size)

    def test_generation_without_duplication(self):
        size = 5
        generator = GrammarGenerator(grammar=self._duplicate_grammar, start=Pixel(), canvas=DummyCanvas(size))
        for iteration in generator.generate(size):
            self.assertEqual(len(iteration), 1)

    def test_existing_pixels_are_retained(self):
        n = 10
        generator = GrammarGenerator(grammar=self._next_diagonal_grammar, start=Pixel(), canvas=DummyCanvas(n + 1))
        # n + 1 because the n iteration add element to start so: n + start
        self.assertEqual(len(list(generator.generate(n))[-1]), n + 1)


if __name__ == '__main__':
    unittest.main()
