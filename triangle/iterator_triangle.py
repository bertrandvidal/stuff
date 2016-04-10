import os
import sys
import time

start = time.time()
text_triangle_path = sys.argv[1] if len(sys.argv) == 2 else "big_triangle.txt"

print "iterator using '%s'" % text_triangle_path

file_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         text_triangle_path))


# method to integerify each entry in the file
def clean_line(text_line):
    return [int(e.strip()) for e in text_line.split(" ")]


class TriangleIterator(object):
    def __init__(self, l):
        self.value = 0
        self.ite = iter(l)

    def __iter__(self):
        return self

    def next(self):
        left = self.value
        self.value = next(self.ite)
        return left, self.value


values = []

with open(file_path, "r") as triangle_file:
    for line in map(clean_line, triangle_file.readlines()):
        result = []
        triangle_ite = TriangleIterator(values)
        for value in line:
            try:
                m = max(next(triangle_ite))
            except StopIteration:
                m = 0
            result.append(value + m)
        values = result

print "max %s in %s" % (max(values), time.time() - start)
