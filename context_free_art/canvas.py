import os
import sys
from dataclasses import dataclass
from io import TextIOWrapper
from typing import List, Tuple

from pixel import Pixel


class Canvas:
    """
    Define basic behavior to display a set of Pixels
    """

    def display(self, pixels: List[Pixel]):
        raise NotImplementedError()

    def dimension(self) -> Tuple[int, int]:
        """
        :return: (width, height) of the display area
        """
        raise NotImplementedError()


@dataclass
class Terminal(Canvas):
    """
    Canvas Pixels in a terminal
    """
    size: int
    output_stream: TextIOWrapper = sys.stdout

    def display(self, pixels: List[Pixel]):
        points = {(p.x, p.y): p for p in pixels}
        for y in range(self.size - 1, -1, -1):
            for x in range(self.size):
                print("X" if (x, y) in points else " ", end="", file=self.output_stream, flush=True)
            print("\n", end="", file=self.output_stream)

    def dimension(self) -> Tuple[int, int]:
        return self.size, self.size


@dataclass
class RgbImage(Canvas):
    """
    Output pixels to an RGB image
    """
    width: int
    height: int
    output_path: os.PathLike

    def display(self, pixels: List[Pixel]):
        pass

    def dimension(self) -> Tuple[int, int]:
        pass
