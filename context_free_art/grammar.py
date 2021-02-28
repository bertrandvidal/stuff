from dataclasses import dataclass
from typing import Callable, List

from display import Display
from pixel import Pixel

# Define the interface for a transformation rule applied to Pixels
Rule = Callable[[Pixel], List[Pixel]]


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
    display: Display

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
                        for p in rule(pixel):
                            if 0 <= p.x < width and 0 <= p.y < height:
                                generated_pixels.add(p)
                yield set(generated_pixels)

        return _iterator()
