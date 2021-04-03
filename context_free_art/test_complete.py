import unittest
from random import randint
from typing import List

from canvas import Terminal
from grammar import Grammar, GrammarGenerator, Rule
from pixel import Pixel


class RandomRule(Rule):

    def __call__(self, pixel: Pixel, width: int, height: int) -> List[Pixel]:
        return [pixel, Pixel(x=pixel.x + randint(-1, 1), y=pixel.y + randint(-1, 1))]


class CompleteTest(unittest.TestCase):

    def test_something(self):
        size = 25
        start = Pixel()
        canvas = Terminal(size)
        rules = [RandomRule()]
        grammar = Grammar(rules)
        generator = GrammarGenerator(grammar, start, canvas)
        for generated_pixels in generator.generate(50):
            print("-" * 25)
            canvas.display(generated_pixels)
            print("-" * 25)
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
