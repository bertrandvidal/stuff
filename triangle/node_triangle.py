import os
import sys
import time

start = time.time()
triangle_file = sys.argv[1] if len(sys.argv) == 2 else "big_triangle.txt"

print "node using '%s'" % triangle_file

file_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         triangle_file))


# method to integerify each entry in the file
def clean_line(line):
    return [int(e.strip()) for e in line.split(" ")]


values = []


class Node(object):
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.best_max = None
        self.nb_visit = 0

    def __str__(self):
        return "[%s/%s] l: %s - r: %s" % (self.value, self.best_max,
                                          self.left.value if self.left is not
                                                             None else "*",
                                          self.right.value if self.right is
                                                              not None else "*")


def get_max(current_node):
    if current_node.best_max is not None:
        return current_node.best_max
    current_node.nb_visit += 1
    left = get_max(current_node.left) if current_node.left is not None else 0
    right = get_max(current_node.right) if current_node.right is not None else 0
    current_node.best_max = current_node.value + max(left, right)
    return current_node.best_max


# triangle is a list of list containing the numbers
with open(file_path, "r") as triangle_file:
    for line in triangle_file.readlines():
        for nb in clean_line(line):
            n = Node(nb)
            values.append(n)

max_len = len(values)
left_index = 1
current = 0
nb_node = 1
node_limit = 1

while left_index + 1 < max_len:
    node = values[current]
    node.left = values[left_index]
    node.right = values[left_index + 1]
    left_index += 1
    current += 1
    nb_node += 1
    if nb_node >= node_limit:
        nb_node = 0
        node_limit += 1
        left_index += 1

print "max %s in %s" % (get_max(values[0]), time.time() - start)
print "average nb visit per node %s" % (sum(x.nb_visit for x in values))

