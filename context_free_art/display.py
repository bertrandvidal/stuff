import sys
from dataclasses import dataclass
from typing import List

from pixel import Pixel


class Display:
    """
    Define basic behavior to display a set of Pixels
    """

    def display(self, pixels: List[Pixel]):
        raise NotImplementedError()


@dataclass
class Terminal(Display):
    """
    Display Pixels in a terminal
    """
    size: int
    output_stream = sys.stdout

    def display(self, pixels: List[Pixel]):
        points = {(p.x, p.y): p for p in pixels}
        for y in range(self.size, 0, -1):
            for x in range(self.size):
                print("X" if (x, y) in points else " ", file=self.output_stream)
