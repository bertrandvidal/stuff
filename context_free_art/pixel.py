from dataclasses import dataclass


@dataclass(frozen=True)
class Pixel:
    """
    Represent the pixel of an image with position and (r,g,b) color.
    The class is immutable and leverages the various tools of `dataclass` to define special methods.
    """
    x: int = 0
    y: int = 0
    r: int = 255
    g: int = 255
    b: int = 255
