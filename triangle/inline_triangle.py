import os
import sys
import time

start = time.time()
text_triangle_path = sys.argv[1] if len(sys.argv) == 2 else "big_triangle.txt"

print "inline using '%s'" % text_triangle_path

file_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         text_triangle_path))


# method to integerify each entry in the file
def clean_line(text_line):
    return [int(e.strip()) for e in text_line.split(" ")]


def compute(top, bottom):
    top.append(0)
    for i, value in enumerate(bottom):
        bottom[i] = value + max(top[i], top[i - 1])
    return bottom


values = []
with open(file_path, "r") as triangle_file:
    for line in map(clean_line, triangle_file.readlines()):
        values = compute(values, line)

print "max %s in %s" % (max(values), time.time() - start)
