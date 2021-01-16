#!/usr/bin/env python

import sys

from PIL import Image

width = None
height = None

with Image.open(sys.argv[1]) as img:
    # convert image to 1-bit B&W image
    bw_image = img.convert()

(width, height) = bw_image.size

min_max = []

for w in range(width):
    max_h = 0
    min_h = height
    for h in range(height):
        (r, g, b, _) = bw_image.getpixel((w, h))
        if r + g + b != 0:
            max_h = max(max_h, h)
            min_h = min(min_h, h)
    if min_h > max_h:
        # w pixel column only has black pixels
        min_h = max_h = 0

    assert min_h <= max_h, f"{w} x {h}: {min_h} / {max_h}"
    min_max.append((min_h, max_h))
