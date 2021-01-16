#!/usr/bin/env python

import sys

import numpy as np
from PIL import Image

width = None
height = None
sampleRate = 48000
duration = 3
frequency = 440.0

bw_image = None

with Image.open(sys.argv[1]) as img:
    # convert image to 1-bit B&W image
    bw_image = img.convert("1")

(width, height) = bw_image.size

min_max = []

# Note that (0, 0) is upper left corner as per
# https://pillow.readthedocs.io/en/4.0.x/handbook/concepts.html#coordinate-system
# So when we are looking for the highest non black pixel it actually has the lowest h
for w in range(width):
    max_h = height
    min_h = 0
    for h in range(height):
        pixel_value = bw_image.getpixel((w, h))
        if pixel_value != 0:
            max_h = min(max_h, h)
            min_h = max(min_h, h)
    # that one is weird but again that's because (0, 0) is upper left of image
    if min_h < max_h:
        # w pixel column only has black pixels
        min_h = max_h = 0

    min_max.append((min_h, max_h))

# each column of the image will be "stretched" to this many "frame" of the wave file
wave_frame = int(duration * sampleRate / len(min_max))
image_range = height
# range of a 16-bit wave
wave_min = -32768
wave_max = 32767
wave_range = wave_max - wave_min


def image_to_wave_scale(v):
    return int(v * wave_range / image_range) + wave_min


def scale(v, from_min, from_max, to_min, to_max):
    """Scaled and clamped value"""
    scaled_value = int(
        to_min + (((v - from_min) / (from_max - from_min)) * (to_max - to_min)))
    return clamp(scaled_value, to_min, to_max)


def clamp(value, to_min, to_max):
    return max(min(value, to_max - 1), to_min + 1)


prev_avg = 0
prev_idx = 0
wave_values = []

viz_w, viz_h = (8192, 2880)
viz_img = Image.new("RGB", (viz_w, viz_h))
idx_range = len(min_max)
viz_frame = int(viz_w / idx_range)

for idx, (min_val, max_val) in enumerate(min_max):
    original_average = max_val + int((min_val - max_val) / 2)
    viz_avg = scale(original_average, 0, height, 0, viz_h)
    # Add min/max/avg in wave_viz_img for visual debugging!!!
    viz_idx = scale(idx, 0, idx_range, 0, viz_w)
    viz_img.putpixel((viz_idx, scale(min_val, 0, height, 0, viz_h)), (0, 255, 0))
    viz_img.putpixel((viz_idx, scale(max_val, 0, height, 0, viz_h)), (255, 0, 0))
    viz_img.putpixel((viz_idx, viz_avg), (0, 0, 255))
    viz_increment_per_step = (viz_avg - prev_avg) / viz_frame
    for viz_step in range(viz_frame + 1):
        viz_img.putpixel(
            (prev_idx + viz_step, prev_avg + int(viz_step * viz_increment_per_step)),
            (255, 255, 0))
    prev_avg = viz_avg
    prev_idx = viz_idx

with open("wave-debug-%s" % sys.argv[1], "wb") as wave_dbg_file:
    viz_img.save(wave_dbg_file)
