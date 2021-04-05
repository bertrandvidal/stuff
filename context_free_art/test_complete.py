import os
import tempfile
import unittest
from random import randint
from typing import List

from canvas import Terminal, Canvas, RgbImage
from grammar import Grammar, GrammarGenerator, Rule
from pixel import Pixel


class RandomRule(Rule):

    def __init__(self, max_rand=1):
        self.max_rand = max_rand

    def __call__(self, pixel: Pixel, canvas: Canvas) -> List[Pixel]:
        return [Pixel(x=pixel.x + randint(-self.max_rand, self.max_rand),
                      y=pixel.y + randint(-self.max_rand, self.max_rand))]


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

    def test_rgb_image(self):
        size = 256
        start = Pixel()
        (_, output_path) = tempfile.mkstemp(suffix=".png")
        canvas = RgbImage(size, size, output_path)
        try:
            rules = [RandomRule(5)]
            grammar = Grammar(rules)
            generator = GrammarGenerator(grammar, start, canvas)
            for i in generator.generate(100):
                print(i)
            canvas.display(generator.generated_pixels)
            self.assertTrue(os.path.isfile(output_path))
        finally:
            if os.path.isfile(output_path):
                os.unlink(output_path)


if __name__ == '__main__':
    unittest.main()
