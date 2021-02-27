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
