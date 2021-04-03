from dataclasses import dataclass
from typing import List, Callable

from canvas import Canvas
from pixel import Pixel


class Rule(Callable):
    """
    Define interface for rules applied to Pixel, default implementation returns the given Pixel unchanged
    """

    def __call__(self, pixel: Pixel, width: int, height: int) -> List[Pixel]:
        return [pixel]


@dataclass
class Grammar:
    """
    Contains the set of Rules that define the entirety of the Grammar.
    """
    rules: List[Callable[[Pixel, int, int], List[Pixel]]]


@dataclass
class GrammarGenerator:
    """
    Given a Grammar and a starting point (a Pixel) generate an iterator for all sequences of the Grammar.
    """
    grammar: Grammar
    start: Pixel
    display: Canvas

    def generate(self, n):
        """
        Generate n iterations for the Grammar

        :return: iterator for n sequences of the grammar
        """

        def _iterator():
            generated_pixels = [self.start]
            width, height = self.display.dimension()
            for _ in range(n):
                pixels = generated_pixels
                generated_pixels = set()
                for pixel in pixels:
                    for rule in self.grammar.rules:
                        for p in rule(pixel, width, height):
                            if 0 <= p.x < width and 0 <= p.y < height:
                                generated_pixels.add(p)
                if generated_pixels:
                    yield generated_pixels

        return _iterator()
