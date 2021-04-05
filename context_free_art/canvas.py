import os
import sys
from dataclasses import dataclass
from io import TextIOWrapper
from typing import List, Tuple

from PIL import Image
from pixel import Pixel


class Canvas:
    """
    Define basic behavior to canvas a set of Pixels
    """

    def display(self, pixels: List[Pixel]):
        raise NotImplementedError()

    def dimension(self) -> Tuple[int, int]:
        """
        :return: (width, height) of the canvas area
        """
        raise NotImplementedError()

    def contains(self, pixel: Pixel) -> bool:
        """ Check if the given pixel is contained in the canvas.
        Provide a simple default implementation such that the pixel is contained in the canvas if:
            0 <= pixel.x < width and 0 <= pixel.y < height

        :param pixel: Pixel to check
        :return: whether or not the given Pixel is in the canvas
        """
        width, height = self.dimension()
        return 0 <= pixel.x < width and 0 <= pixel.y < height


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
    output_path: str

    def display(self, pixels: List[Pixel]):
        image = Image.new("RGB", self.dimension())
        for p in pixels:
            image.putpixel((p.x, p.y), (p.r, p.g, p.b))
        image.show()
        with open(self.output_path, "wb") as image_file:
            image.save(image_file)

    def dimension(self) -> Tuple[int, int]:
        return self.width, self.height
