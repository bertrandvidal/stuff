#!/usr/bin/env python

import sys

from PIL import Image

width = None
height = None
sampleRate = 48000
duration = 3
frequency = 440.0

bw_image = None
debug_image = None

with Image.open(sys.argv[1]) as img:
    # convert image to 1-bit B&W image
    bw_image = img.convert("1")
    debug_image = img.copy()

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
    # mark the top pixel with red and lower with green #visualdebug
    debug_image.putpixel((w, max_h), (255, 0, 0))
    debug_image.putpixel((w, min_h), (0, 255, 0))

    assert min_h >= max_h, f"{w} x {h}: {min_h} / {max_h}"
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
    return int(to_min + (
            ((v - from_min) / (from_max - from_min))
            * (to_max - to_min)
    ))


prev_avg = 0
wave_values = []
for idx, (min_val, max_val) in enumerate(min_max):
    original_average = max_val + int((min_val - max_val) / 2)
    debug_image.putpixel((idx, original_average), (0, 0, 255))
    scaled_avg = scale(original_average, 0, height, wave_min, wave_max)
    # we gradually go from the previous avg to the current one
    per_frame_diff = int((scaled_avg - prev_avg) / wave_frame)
    for frame in range(wave_frame):
        value = prev_avg + (frame * per_frame_diff)
        if value > wave_max or value < wave_min:
            print(f"bad value: {value} @ index {idx} @ frame {frame}")
        wave_values.append(value)
    prev_avg = scaled_avg

with open("debug-%s" % sys.argv[1], "wb") as dbg_file:
    debug_image.save(dbg_file)

wave_viz_w, wave_viz_h = (int(len(wave_values) / 8), int(wave_range / 100))
# Entirely black image
wave_visualization = Image.new("RGB", (wave_viz_w, wave_viz_h), color=0)

with open("wave-debug-%s" % sys.argv[1], "wb") as wave_dbg_file:
    # we "sample" the wave values to adapt to the wave_viz width
    for idx, wave_value in enumerate(wave_values[:wave_viz_w]):
        try:
            wave_viz_value = scale(wave_value, wave_min, wave_max, 0, wave_viz_h)
            wave_visualization.putpixel((idx, wave_viz_value),
                                        (0, 255, 255))
        except Exception as e:
            print(f"@{idx}: scale({wave_value}) = {wave_viz_value}")
            raise e
    wave_visualization.save(wave_dbg_file)
