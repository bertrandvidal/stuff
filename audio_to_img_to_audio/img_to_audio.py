#!/usr/bin/env python
import struct
import sys
import wave

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


def image_to_wave_scale(v):
    return int(v * wave_range / image_range) + wave_min


def scale(v, from_min, from_max, to_min, to_max):
    """Scaled and clamped value"""
    scaled_value = int(
        to_min + (((v - from_min) / (from_max - from_min)) * (to_max - to_min)))
    return clamp(scaled_value, to_min, to_max)


def clamp(value, to_min, to_max):
    return max(min(value, to_max - 1), to_min + 1)


viz_prev_avg = 0
viz_prev_idx = 0
viz_w, viz_h = (8192, 2880)
viz_img = Image.new("RGB", (viz_w, viz_h))
idx_range = len(min_max)
viz_frame = int(viz_w / idx_range)

# each column of the image will be "stretched" to this many "frame" of the wave file
wave_length = int(duration * sampleRate)
wave_frame = int(wave_length / idx_range)
image_range = height
# range of a 16-bit wave
wave_min = -32768
wave_max = 32767
wave_range = wave_max - wave_min
wave_prev_avg = 0
wave_values = []

for idx, (min_val, max_val) in enumerate(min_max):
    original_average = max_val + int((min_val - max_val) / 2)
    viz_avg = scale(original_average, 0, height, 0, viz_h)
    # Add min/max/avg in wave_viz_img for visual debugging!!!
    viz_idx = scale(idx, 0, idx_range, 0, viz_w)
    viz_img.putpixel((viz_idx, scale(min_val, 0, height, 0, viz_h)), (0, 255, 0))
    viz_img.putpixel((viz_idx, scale(max_val, 0, height, 0, viz_h)), (255, 0, 0))
    viz_img.putpixel((viz_idx, viz_avg), (0, 0, 255))
    viz_increment_per_step = (viz_avg - viz_prev_avg) / viz_frame
    for viz_step in range(viz_frame + 1):
        viz_img.putpixel(
            (viz_prev_idx + viz_step, viz_prev_avg + int(viz_step * viz_increment_per_step)),
            (255, 255, 0))
    viz_prev_avg = viz_avg
    viz_prev_idx = viz_idx
    # Handle wave's values
    wave_avg = scale(original_average, 0, height, wave_min, wave_max)
    wave_increment_per_step = (wave_avg - wave_prev_avg) / wave_frame
    for wave_step in range(wave_frame + 1):
        wave_values.append(wave_prev_avg + int(wave_step * wave_increment_per_step))
    wave_values.append(wave_avg)
    wave_prev_avg = wave_avg

with open("wave-debug-%s" % sys.argv[1], "wb") as wave_dbg_file:
    viz_img.save(wave_dbg_file)

with wave.open("output-%s.wav" % sys.argv[1], 'w') as wave_file:
    wave_file.setnchannels(1)  # mono
    wave_file.setsampwidth(2)
    wave_file.setframerate(sampleRate)
    for wave_value in wave_values:
        wave_file.writeframesraw(struct.pack('<h', int(wave_value)))
