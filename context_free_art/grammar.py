from dataclasses import dataclass
from typing import List, Callable

from canvas import Canvas
from pixel import Pixel


class Rule(Callable):
    """
    Define interface for rules applied to Pixel, default implementation returns the given Pixel unchanged
    """

    def __call__(self, pixel: Pixel, canvas: Canvas) -> List[Pixel]:
        return [pixel]


@dataclass
class LambdaRule(Rule):
    _lambda: Callable[[Pixel, Canvas], List[Pixel]] = lambda x, c: x

    def __call__(self, pixel: Pixel, canvas: Canvas) -> List[Pixel]:
        return self._lambda(pixel, canvas)


@dataclass
class Grammar:
    """
    Contains the set of Rules that define the entirety of the Grammar.
    """
    rules: List[Rule]


@dataclass
class GrammarGenerator:
    """
    Given a Grammar and a starting point (a Pixel) generate an iterator for all sequences of the Grammar.
    """
    grammar: Grammar
    start: Pixel
    canvas: Canvas

    def generate(self, n):
        """
        Generate n iterations for the Grammar

        :return: iterator for n sequences of the grammar
        """

        def _iterator():
            generated_pixels = [self.start]
            for _ in range(n):
                pixels = generated_pixels
                generated_pixels = set()
                for pixel in pixels:
                    for rule in self.grammar.rules:
                        for p in rule(pixel, self.canvas):
                            if self.canvas.contains(p):
                                generated_pixels.add(p)
                if generated_pixels:
                    yield generated_pixels

        return _iterator()
