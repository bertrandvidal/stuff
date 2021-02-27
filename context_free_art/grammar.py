from dataclasses import dataclass
from typing import Callable, List

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

    def generate(self, n):
        """
        Generate n iterations for the Grammar

        :return: iterator for n sequences of the grammar
        """
        def _iterator():
            generated_pixels = [self.start]
            for _ in range(n):
                pixels = generated_pixels
                generated_pixels = []
                for pixel in pixels:
                    for rule in self.grammar.rules:
                        generated_pixels.extend(rule(pixel))
                yield set(generated_pixels)

        return _iterator()
