#!/usr/bin/env python

import struct
import sys
import wave

from PIL import Image

width = None
height = None
sampleRate = 48000
duration = 3
frequency = 440.0

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

# each column of the image will be "stretched" to this many "frame" of the wave file
wave_frame = int(duration * sampleRate / len(min_max))
image_range = height
# as per http://soundfile.sapp.org/doc/WaveFormat/, see 8-bit sample
wave_range = 255

scale_value = lambda v: int(v * wave_range / image_range)

with wave.open("output-%s.wav" % sys.argv[1], 'w') as wave_file:
    wave_file.setnchannels(1)  # mono
    wave_file.setsampwidth(2)
    wave_file.setframerate(sampleRate)
    for idx, (min_val, max_val) in enumerate(min_max):
        value = min_val if idx % 2 == 0 else max_val
        scaled_value = scale_value(value)
        # we repeat that same value 'wave_frame' time in the file
        for _ in range(wave_frame):
            data = struct.pack('<h', scaled_value)
            wave_file.writeframesraw(data)
