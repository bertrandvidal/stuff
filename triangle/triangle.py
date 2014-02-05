import os
import sys

triangle_file = sys.argv[1] if len(sys.argv) == 2 else "big_triangle.txt"

print "Using '%s'" % triangle_file

file_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         triangle_file))

# method to integerify each entry in the file
def clean_line(line):
  return [int(e.strip()) for e in line.split(" ")]

# triangle is a list of list containing the numbers
with open(file_path, "r") as triangle_file:
  triangle = map(clean_line, triangle_file.readlines())

# base maintains the current 'total'
base = triangle.pop(0)

# Each line of the triangle is modified inline which forces us to copy
# the line back into base
for line in triangle:
  # We add this extra entry so we can use the trick where list[-1] is
  # the last element of the list
  base.append(0)
  for index, entry in enumerate(line):
    # The current entry is added to the max between the number directly
    # above and the number above and one to the left - potentially the
    # last number of the list when index - 1 = -1
    line[index] = entry + max(base[index], base[index -1])
  base = line[:]

print max(base)
