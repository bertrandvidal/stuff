#!/usr/bin/env python
import struct
import sys
import wave

import numpy as np
from PIL import Image

width = None
height = None
sampleRate = 48000
duration = 1.5
frequency = 440.0
border_skip = 10
min_max = []
bw_image = None

original_file_name = sys.argv[1]
original_file_format = None


def scale(v, from_min, from_max, to_min, to_max):
    """Scaled and clamped value"""
    scaled_value = int(
        to_min + (((v - from_min) / (from_max - from_min)) * (to_max - to_min)))
    return clamp(scaled_value, to_min, to_max)


def clamp(value, to_min, to_max):
    return max(min(value, to_max - 1), to_min + 1)


with Image.open(original_file_name) as img:
    # convert image to 1-bit B&W image
    bw_image = img.convert("L")
    original_file_format = img.format
(width, height) = bw_image.size

# TODO(bvidal): Ideas
# [] input/output folder
# [] dockerize
# [] do not collect min/max to get avg rather take pixel with highest intensity
# [] using sin wave/numpy to link timeseries rather than linear

# Note that (0, 0) is upper left corner as per
# https://pillow.readthedocs.io/en/4.0.x/handbook/concepts.html#coordinate-system
# So when we are looking for the highest non black pixel it actually has the lowest h
for w in range(width):
    max_h = height
    min_h = 0
    # We skip the very top and bottom where there often is noise
    for h in range(border_skip, height - border_skip):
        # The x-axis is left on the screenshot so we ignore it when collecting
        # min/max
        if h == height/2:
            continue
        pixel_value = bw_image.getpixel((w, h))
        if pixel_value > 50:
            max_h = min(max_h, h)
            min_h = max(min_h, h)
    # that one is weird but again that's because (0, 0) is upper left of image
    if min_h < max_h:
        # w pixel column only has black pixels
        min_h = max_h = 0

    min_max.append((min_h, max_h))

viz_prev_avg = 0
viz_prev_idx = 0
viz_w, viz_h = (4096, 1440)
viz_img = Image.new("RGB", (viz_w, viz_h))
idx_range = len(min_max)
viz_frame = int(viz_w / idx_range)

# each column of the image will be "stretched" to this many "frame" of the wav file
wav_length = int(duration * sampleRate)
wav_frame = int(wav_length / idx_range)
image_range = height
# range of a 16-bit wav
wav_interval_min = -32768
wav_interval_max = 32767
wav_min = wav_interval_max
wav_max = wav_interval_min
wav_range = wav_interval_max - wav_interval_min
wav_prev_avg = 0
wav_values = []

for idx, (min_val, max_val) in enumerate(min_max):
    original_average = max_val + int((min_val - max_val) / 2)
    viz_avg = scale(original_average, 0, height, 0, viz_h)
    # Add min/max/avg in wav_viz_img for visual debugging!!!
    viz_idx = scale(idx, 0, idx_range, 0, viz_w)
    viz_img.putpixel((viz_idx, scale(min_val, 0, height, 0, viz_h)), (0, 255, 0))
    viz_img.putpixel((viz_idx, scale(max_val, 0, height, 0, viz_h)), (255, 0, 0))
    viz_img.putpixel((viz_idx, viz_avg), (0, 0, 255))
    viz_increment_per_step = (viz_avg - viz_prev_avg) / viz_frame
    for viz_step in range(viz_frame + 1):
        viz_img.putpixel(
            (viz_prev_idx + viz_step,
             viz_prev_avg + int(viz_step * viz_increment_per_step)),
            (255, 255, 0))
    viz_prev_avg = viz_avg
    viz_prev_idx = viz_idx
    # Handle wav's values
    wav_avg = scale(original_average, 0, height, wav_interval_min,
                     wav_interval_max)
    wav_min = min(wav_min, wav_avg)
    wav_max = max(wav_max, wav_avg)
    wav_increment_per_step = (wav_avg - wav_prev_avg) / wav_frame
    for wav_step in range(wav_frame + 1):
        wav_values.append(wav_prev_avg + int(wav_step * wav_increment_per_step))
    wav_values.append(wav_avg)
    wav_prev_avg = wav_avg

with open(f"{original_file_name}-viz-debug.{original_file_format}", "wb") as \
        viz_dbg_file:
    viz_img.save(viz_dbg_file)

wav_viz_width_ratio = 25
wav_viz_height_ratio = 25
wav_viz_width = int(len(wav_values) / wav_viz_width_ratio)
wav_viz_height = int(
    (wav_interval_max - wav_interval_min) / wav_viz_height_ratio)
wav_viz_img = Image.new("RGB", (wav_viz_width, wav_viz_height))

for wav_viz_idx, wave_value in enumerate(wav_values[::wav_viz_width_ratio]):
    wav_viz_value = scale(wave_value, wav_interval_min, wav_interval_max, 0,
                          wav_viz_height)
    wav_viz_img.putpixel((min(wav_viz_idx, wav_viz_width - 1), wav_viz_value),
                         (0, 255, 255))

with open(f"{original_file_name}-wav-debug.{original_file_format}", "wb") as \
        wav_dbg_file:
    wav_viz_img.save(wav_dbg_file)

wav_np_int_values = np.array(wav_values, dtype="int16")
with wave.open(f"{original_file_name}-output.wav", 'wb') as wav_file:
    wav_file.setnchannels(1)  # mono
    # https://docs.python.org/3/library/wave.html#wave.Wave_write.setsampwidth: "Set
    # the sample width to n bytes." and
    # https://www.metadata2go.com/result/2728f923-05ac-43ed-a413-cf3ff59e6689
    # shows 32 bits per sample => 4 bytes
    wav_file.setsampwidth(4)
    wav_file.setframerate(sampleRate)  # obtain from audio software
    for wav_value in wav_np_int_values:
        wav_file.writeframesraw(struct.pack('h', wav_value))
